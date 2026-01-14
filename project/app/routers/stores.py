from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Store, store_services, User
from app.schemas import StoreResponse, StoreCreate, StoreUpdate
from app.dependencies import get_current_user, require_permission
from app.utils.geocoding import geocode_address
from app.utils.cache import cache

router = APIRouter(prefix="/api/stores", tags=["Stores"])


@router.get("/", response_model=List[StoreResponse])
def get_all_stores(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("read:stores"))
):
    """Get all stores with pagination (requires authentication)"""
    stores = db.query(Store).offset(skip).limit(limit).all()

    # Fetch services for each store
    result = []
    for store in stores:
        store_dict = store.__dict__.copy()
        # Get services from association table
        services = db.execute(
            store_services.select().where(store_services.c.store_id == store.store_id)
        ).fetchall()
        store_dict['services'] = [s.service_name for s in services]
        result.append(store_dict)

    return result


@router.get("/{store_id}", response_model=StoreResponse)
def get_store(
    store_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("read:stores"))
):
    """Get a single store by ID (requires authentication)"""
    store = db.query(Store).filter(Store.store_id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    # Get services
    services = db.execute(
        store_services.select().where(store_services.c.store_id == store.store_id)
    ).fetchall()

    store_dict = store.__dict__.copy()
    store_dict['services'] = [s.service_name for s in services]

    return store_dict


@router.post("/", response_model=StoreResponse, status_code=status.HTTP_201_CREATED)
def create_store(
    store_data: StoreCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("write:stores"))
):
    """Create a new store (requires write:stores permission - Admin or Marketer only)"""
    # Check if store_id already exists
    existing = db.query(Store).filter(Store.store_id == store_data.store_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Store ID already exists")

    # Extract services
    services_list = store_data.services
    store_dict = store_data.model_dump()
    del store_dict['services']

    # Auto-geocode if coordinates are missing but address is present
    if (store_dict.get('latitude') is None or store_dict.get('longitude') is None) and \
       (store_dict.get('address_street') and store_dict.get('address_city') and store_dict.get('address_state')):
        full_address = f"{store_dict['address_street']}, {store_dict['address_city']}, {store_dict['address_state']}"
        geo = geocode_address(full_address)
        if geo:
            store_dict['latitude'] = geo['latitude']
            store_dict['longitude'] = geo['longitude']

    # Default status to active if not provided
    if not store_dict.get('status'):
        store_dict['status'] = 'active'
    
    # Generate store_id if not provided (simple increment for demo, ideally UUID or sequence)
    # For now, we rely on the user providing it or we could generate one. 
    # The current schema requires store_id. Let's assume user provides it (as per the JSON example).

    # Create store
    new_store = Store(**store_dict)
    db.add(new_store)
    db.flush()

    # Invalidate search cache
    cache.clear() 

    # Add services
    for service in services_list:
        db.execute(
            store_services.insert().values(
                store_id=new_store.store_id,
                service_name=service
            )
        )

    db.commit()
    db.refresh(new_store)

    result = new_store.__dict__.copy()
    result['services'] = services_list

    return result


@router.patch("/{store_id}", response_model=StoreResponse)
def update_store(
    store_id: str,
    store_data: StoreUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("write:stores"))
):
    """Partially update a store (requires write:stores permission - Admin or Marketer only)"""
    store = db.query(Store).filter(Store.store_id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    # Update only provided fields
    update_data = store_data.model_dump(exclude_unset=True)

    # Handle services separately
    services_list = None
    if 'services' in update_data:
        services_list = update_data.pop('services')
        # Delete existing services
        db.execute(
            store_services.delete().where(store_services.c.store_id == store_id)
        )
        # Add new services
        for service in services_list:
            db.execute(
                store_services.insert().values(
                    store_id=store_id,
                    service_name=service
                )
            )

    # Update store fields
    for field, value in update_data.items():
        setattr(store, field, value)

    db.commit()
    cache.clear() # Invalidate cache on update
    db.refresh(store)

    # Get current services
    if services_list is None:
        services = db.execute(
            store_services.select().where(store_services.c.store_id == store_id)
        ).fetchall()
        services_list = [s.service_name for s in services]

    result = store.__dict__.copy()
    result['services'] = services_list

    return result


@router.delete("/{store_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_store(
    store_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("delete:stores"))
):
    """Soft delete a store (requires delete:stores permission - Admin or Marketer only)"""
    store = db.query(Store).filter(Store.store_id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    # Soft delete
    # Soft delete
    store.status = "inactive"
    db.commit()
    cache.clear() # Invalidate cache on delete

    return None
