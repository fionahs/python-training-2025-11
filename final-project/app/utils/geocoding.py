from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from app.config import get_settings
from app.utils.cache import cache, GEOCODING_TTL

settings = get_settings()

# Initialize geocoder
geolocator = Nominatim(user_agent=settings.GEOCODING_USER_AGENT)


def geocode_address(address: str) -> dict:
    """
    Convert an address to coordinates using Nominatim (free geocoding service).
    Results are cached for 30 days to reduce API calls.

    Args:
        address: Full address string

    Returns:
        dict with 'latitude' and 'longitude', or None if geocoding fails
    """
    # Check cache first
    cache_key = f"geocode:address:{address.lower()}"
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return cached_result

    # Cache miss - call geocoding API
    try:
        location = geolocator.geocode(address, timeout=10)
        if location:
            result = {
                "latitude": location.latitude,
                "longitude": location.longitude,
                "formatted_address": location.address
            }
            # Cache the result for 30 days
            cache.set(cache_key, result, GEOCODING_TTL)
            return result
        return None
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        print(f"Geocoding error: {e}")
        return None


def geocode_postal_code(postal_code: str, country: str = "USA") -> dict:
    """
    Convert a postal code to coordinates.

    Args:
        postal_code: ZIP code
        country: Country code (default: USA)

    Returns:
        dict with 'latitude' and 'longitude', or None if geocoding fails
    """
    query = f"{postal_code}, {country}"
    return geocode_address(query)
