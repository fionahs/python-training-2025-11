from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
import json
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.database import get_db
from app.models import Store, store_services
from app.schemas import StoreSearchRequest, StoreSearchResponse, StoreSearchResult, StoreResponse
from app.utils.geocoding import geocode_address, geocode_postal_code
from app.utils.distance import calculate_bounding_box, calculate_distance, is_store_open_now
from app.utils.cache import cache, SEARCH_TTL
from app.config import get_settings

router = APIRouter(prefix="/api/stores", tags=["Store Search"])
limiter = Limiter(key_func=get_remote_address)
settings = get_settings()


def apply_rate_limit(limit_string):
    """Decorator that applies rate limiting only if not in testing mode"""
    def decorator(func):
        if settings.TESTING:
            return func
        return limiter.limit(limit_string)(func)
    return decorator


@router.post("/search", response_model=StoreSearchResponse)
@apply_rate_limit("10/minute")
@apply_rate_limit("100/hour")
def search_stores(request: Request, search_request: StoreSearchRequest, db: Session = Depends(get_db)):
    """
    Search for nearby stores by address, postal code, or coordinates.

    This is a PUBLIC endpoint - no authentication required.
    Results are cached for 5 minutes to improve performance.

    Supports:
    - Search by full address
    - Search by postal code
    - Search by latitude/longitude
    - Filter by radius, services, store types, and open status
    """

    # Check cache first (only for coordinate-based searches, not open_now filters)
    if search_request.latitude and search_request.longitude and not search_request.open_now:
        cache_key = f"search:{search_request.latitude:.4f}:{search_request.longitude:.4f}:{search_request.radius_miles}"
        if search_request.services:
            cache_key += f":{','.join(sorted(search_request.services))}"
        if search_request.store_types:
            cache_key += f":{','.join(sorted([st.value for st in search_request.store_types]))}"

        cached_result = cache.get(cache_key)
        if cached_result is not None:
            print(f"  [DEBUG] Cache HIT for {cache_key}")
            return cached_result

    # Step 1: Get search coordinates
    search_lat = None
    search_lon = None
    search_location_info = {}

    if search_request.latitude and search_request.longitude:
        # Direct coordinates provided
        search_lat = search_request.latitude
        search_lon = search_request.longitude
        search_location_info = {
            "type": "coordinates",
            "latitude": search_lat,
            "longitude": search_lon
        }

    elif search_request.postal_code:
        # Geocode postal code
        result = geocode_postal_code(search_request.postal_code)
        if not result:
            raise HTTPException(
                status_code=400,
                detail=f"Could not geocode postal code: {search_request.postal_code}"
            )
        search_lat = result["latitude"]
        search_lon = result["longitude"]
        search_location_info = {
            "type": "postal_code",
            "postal_code": search_request.postal_code,
            "latitude": search_lat,
            "longitude": search_lon,
            "formatted_address": result.get("formatted_address")
        }

    elif search_request.address:
        # Geocode full address
        result = geocode_address(search_request.address)
        if not result:
            raise HTTPException(
                status_code=400,
                detail=f"Could not geocode address: {search_request.address}"
            )
        search_lat = result["latitude"]
        search_lon = result["longitude"]
        search_location_info = {
            "type": "address",
            "address": search_request.address,
            "latitude": search_lat,
            "longitude": search_lon,
            "formatted_address": result.get("formatted_address")
        }

    else:
        raise HTTPException(
            status_code=400,
            detail="Must provide either address, postal_code, or coordinates (latitude & longitude)"
        )

    # Step 2: Calculate bounding box for efficient database query
    bbox = calculate_bounding_box(search_lat, search_lon, search_request.radius_miles)

    # Step 3: Query database with bounding box filter
    query = db.query(Store).filter(
        Store.latitude.between(bbox["min_lat"], bbox["max_lat"]),
        Store.longitude.between(bbox["min_lon"], bbox["max_lon"]),
        Store.status == "active"  # Only active stores
    )

    # Apply store type filter
    if search_request.store_types:
        query = query.filter(Store.store_type.in_(search_request.store_types))

    stores = query.all()

    # Step 4: Calculate exact distances and filter by radius
    results = []
    for store in stores:
        # Calculate exact distance
        distance = calculate_distance(
            search_lat, search_lon,
            store.latitude, store.longitude
        )

        # Filter by radius
        if distance > search_request.radius_miles:
            continue

        # Get store services
        services = db.execute(
            store_services.select().where(store_services.c.store_id == store.store_id)
        ).fetchall()
        services_list = [s.service_name for s in services]

        # Filter by services (AND logic - store must have ALL requested services)
        if search_request.services:
            if not all(service in services_list for service in search_request.services):
                continue

        # Check if open now
        hours_dict = {
            'hours_mon': store.hours_mon,
            'hours_tue': store.hours_tue,
            'hours_wed': store.hours_wed,
            'hours_thu': store.hours_thu,
            'hours_fri': store.hours_fri,
            'hours_sat': store.hours_sat,
            'hours_sun': store.hours_sun,
        }
        is_open = is_store_open_now(hours_dict)

        # Filter by open_now
        if search_request.open_now and not is_open:
            continue

        # Build store data
        store_dict = store.__dict__.copy()
        store_dict['services'] = services_list

        results.append({
            "store": store_dict,
            "distance_miles": round(distance, 2),
            "is_open_now": is_open
        })

    # Step 5: Sort by distance (nearest first)
    results.sort(key=lambda x: x["distance_miles"])

    # Step 6: Build response
    filters_applied = {
        "radius_miles": search_request.radius_miles,
        "services": search_request.services or [],
        "store_types": [st.value for st in search_request.store_types] if search_request.store_types else [],
        "open_now": search_request.open_now
    }

    response = {
        "results": results,
        "search_location": search_location_info,
        "filters_applied": filters_applied,
        "total_results": len(results)
    }

    # Cache the result (only for coordinate-based searches, not open_now)
    if search_request.latitude and search_request.longitude and not search_request.open_now:
        cache_key = f"search:{search_request.latitude:.4f}:{search_request.longitude:.4f}:{search_request.radius_miles}"
        if search_request.services:
            cache_key += f":{','.join(sorted(search_request.services))}"
        if search_request.store_types:
            cache_key += f":{','.join(sorted([st.value for st in search_request.store_types]))}"
        cache.set(cache_key, response, SEARCH_TTL)

    return response
