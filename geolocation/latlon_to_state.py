# latlon_to_state.py

import pandas as pd
import time
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

print("🚀 Script started: Processing latitude and longitude to state...")  # 👈 Startup message

# Load your cleaned accident data
df = pd.read_csv("C:/Py_Group/roadsafe_ai/data/cleaned_accidents.csv")   # ✅ Adjust path if needed

# Setup Nominatim geolocator
geolocator = Nominatim(user_agent="roadsafe_ai")
geocode = RateLimiter(geolocator.reverse, min_delay_seconds=1)

# Function to reverse geocode and get state
def get_state(row, retries=3, delay=2):
    lat, lon = row['latitude'], row['longitude']
    for attempt in range(retries):
        try:
            location = geocode((lat, lon), language='en')
            if location and 'state' in location.raw['address']:
                return location.raw['address']['state']
            else:
                return "Unknown"
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            print(f"⚠️ Retry {attempt+1}/{retries} for ({lat}, {lon}): {e}")
            time.sleep(delay)
        except Exception as e:
            print(f"❌ Unexpected error at ({lat}, {lon}): {e}")
            return "Unknown"
    return "Unknown"

# Apply to all rows
print("🛰️ Classifying states from lat/lon...")
df['State'] = df.apply(lambda row: get_state(row), axis=1)

# Save updated dataset
df.to_csv("C:/Py_Group/roadsafe_ai/data/raw/accidents_with_states.csv", index=False)
print("✅ States added and saved to data/accidents_with_states.csv")
