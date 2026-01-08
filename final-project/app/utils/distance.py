import math
from geopy.distance import geodesic


def calculate_bounding_box(latitude: float, longitude: float, radius_miles: float) -> dict:
    """
    Calculate bounding box coordinates for a given center point and radius.

    Args:
        latitude: Center point latitude
        longitude: Center point longitude
        radius_miles: Search radius in miles

    Returns:
        dict with min_lat, max_lat, min_lon, max_lon
    """
    # Approximate degrees per mile
    # 1 degree of latitude ≈ 69 miles
    # 1 degree of longitude varies by latitude

    latitude_delta = radius_miles / 69.0
    longitude_delta = radius_miles / (69.0 * math.cos(math.radians(latitude)))

    return {
        "min_lat": latitude - latitude_delta,
        "max_lat": latitude + latitude_delta,
        "min_lon": longitude - longitude_delta,
        "max_lon": longitude + longitude_delta
    }


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two points using Haversine formula (via geopy).

    Args:
        lat1, lon1: First point coordinates
        lat2, lon2: Second point coordinates

    Returns:
        Distance in miles
    """
    point1 = (lat1, lon1)
    point2 = (lat2, lon2)
    return geodesic(point1, point2).miles


def is_store_open_now(hours: dict) -> bool:
    """
    Check if a store is currently open based on hours.

    Args:
        hours: Dictionary with keys like 'hours_mon', 'hours_tue', etc.

    Returns:
        True if store is open now, False otherwise
    """
    from datetime import datetime

    # Get current day and time
    now = datetime.now()
    day_names = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    current_day = day_names[now.weekday()]
    current_time = now.time()

    # Get today's hours
    hours_key = f'hours_{current_day}'
    today_hours = hours.get(hours_key, 'closed')

    if today_hours == 'closed':
        return False

    # Parse hours (format: "HH:MM-HH:MM")
    try:
        open_time_str, close_time_str = today_hours.split('-')
        open_hour, open_min = map(int, open_time_str.split(':'))
        close_hour, close_min = map(int, close_time_str.split(':'))

        open_time = datetime.now().replace(hour=open_hour, minute=open_min, second=0, microsecond=0).time()
        close_time = datetime.now().replace(hour=close_hour, minute=close_min, second=0, microsecond=0).time()

        return open_time <= current_time <= close_time
    except:
        return False
