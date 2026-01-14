from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import sys

def test_geocode():
    ua = "fionas-store-locator-diagnostic-test"
    print(f"Testing Nominatim with User-Agent: {ua}")
    import ssl
    import certifi
    ctx = ssl.create_default_context(cafile=certifi.where())
    geolocator = Nominatim(user_agent=ua, ssl_context=ctx)
    
    address = "100 Cambridge St, Boston, MA"
    try:
        print(f"Attempting to geocode: {address}")
        location = geolocator.geocode(address, timeout=10)
        if location:
            print(f"SUCCESS: {location.address}")
            print(f"Coordinates: {location.latitude}, {location.longitude}")
        else:
            print("FAILURE: Nominatim returned no results for this address.")
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_geocode()
