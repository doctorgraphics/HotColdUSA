import json
import pathlib
from datetime import datetime, timezone

# Define the path where the catalog will be saved
OUTPUT_PATH = pathlib.Path("data/stations.json")

# A list of 50 cities (one per state)
CITIES = [
    {"name": "Montgomery", "state": "AL", "lat": 32.377, "lon": -86.300},
    {"name": "Juneau", "state": "AK", "lat": 58.301, "lon": -134.420},
    {"name": "Phoenix", "state": "AZ", "lat": 33.448, "lon": -112.074},
    {"name": "Little Rock", "state": "AR", "lat": 34.746, "lon": -92.289},
    {"name": "Sacramento", "state": "CA", "lat": 38.576, "lon": -121.493},
    {"name": "Denver", "state": "CO", "lat": 39.739, "lon": -104.990},
    {"name": "Hartford", "state": "CT", "lat": 41.764, "lon": -72.691},
    {"name": "Dover", "state": "DE", "lat": 39.157, "lon": -75.519},
    {"name": "Tallahassee", "state": "FL", "lat": 30.438, "lon": -84.281},
    {"name": "Atlanta", "state": "GA", "lat": 33.749, "lon": -84.388},
    {"name": "Honolulu", "state": "HI", "lat": 21.307, "lon": -157.858},
    {"name": "Boise", "state": "ID", "lat": 43.618, "lon": -116.202},
    {"name": "Springfield", "state": "IL", "lat": 39.799, "lon": -89.646},
    {"name": "Indianapolis", "state": "IN", "lat": 39.768, "lon": -86.158},
    {"name": "Des Moines", "state": "IA", "lat": 41.591, "lon": -93.604},
    {"name": "Topeka", "state": "KS", "lat": 39.048, "lon": -95.678},
    {"name": "Frankfort", "state": "KY", "lat": 38.187, "lon": -84.875},
    {"name": "Baton Rouge", "state": "LA", "lat": 30.457, "lon": -91.187},
    {"name": "Augusta", "state": "ME", "lat": 44.307, "lon": -69.782},
    {"name": "Annapolis", "state": "MD", "lat": 38.978, "lon": -76.492},
    {"name": "Boston", "state": "MA", "lat": 42.360, "lon": -71.058},
    {"name": "Lansing", "state": "MI", "lat": 42.734, "lon": -84.555},
    {"name": "St. Paul", "state": "MN", "lat": 44.953, "lon": -93.090},
    {"name": "Jackson", "state": "MS", "lat": 32.299, "lon": -90.185},
    {"name": "Jefferson City", "state": "MO", "lat": 38.577, "lon": -92.172},
    {"name": "Helena", "state": "MT", "lat": 46.593, "lon": -112.036},
    {"name": "Lincoln", "state": "NE", "lat": 40.809, "lon": -96.675},
    {"name": "Carson City", "state": "NV", "lat": 39.164, "lon": -119.766},
    {"name": "Concord", "state": "NH", "lat": 43.208, "lon": -71.538},
    {"name": "Trenton", "state": "NJ", "lat": 40.221, "lon": -74.756},
    {"name": "Santa Fe", "state": "NM", "lat": 35.687, "lon": -105.939},
    {"name": "Albany", "state": "NY", "lat": 42.653, "lon": -73.755},
    {"name": "Raleigh", "state": "NC", "lat": 35.779, "lon": -78.638},
    {"name": "Bismarck", "state": "ND", "lat": 46.808, "lon": -100.783},
    {"name": "Columbus", "state": "OH", "lat": 39.961, "lon": -82.999},
    {"name": "Oklahoma City", "state": "OK", "lat": 35.468, "lon": -97.516},
    {"name": "Salem", "state": "OR", "lat": 44.943, "lon": -123.035},
    {"name": "Harrisburg", "state": "PA", "lat": 40.273, "lon": -76.887},
    {"name": "Providence", "state": "RI", "lat": 41.824, "lon": -71.412},
    {"name": "Columbia", "state": "SC", "lat": 33.999, "lon": -81.035},
    {"name": "Pierre", "state": "SD", "lat": 44.368, "lon": -100.351},
    {"name": "Nashville", "state": "TN", "lat": 36.163, "lon": -86.782},
    {"name": "Austin", "state": "TX", "lat": 30.267, "lon": -97.743},
    {"name": "Salt Lake City", "state": "UT", "lat": 40.761, "lon": -111.891},
    {"name": "Montpelier", "state": "VT", "lat": 44.260, "lon": -72.575},
    {"name": "Richmond", "state": "VA", "lat": 37.541, "lon": -77.436},
    {"name": "Olympia", "state": "WA", "lat": 47.038, "lon": -122.901},
    {"name": "Charleston", "state": "WV", "lat": 38.350, "lon": -81.632},
    {"name": "Madison", "state": "WI", "lat": 43.073, "lon": -89.401},
    {"name": "Cheyenne", "state": "WY", "lat": 41.140, "lon": -104.820}
]

def main():
    print(f"Generating city catalog with {len(CITIES)} locations...")
    
    stations = []
    for city in CITIES:
        # We use .get() here as a safety measure to prevent future KeyErrors
        name = city.get("name", "Unknown")
        state = city.get("state", "??")
        
        stations.append({
            "station": f"{state}_{name.replace(' ', '')}",
            "name": name,
            "state": state,
            "latitude": city.get("lat"),
            "longitude": city.get("lon")
        })

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "description": "50 US Cities (One per State)",
        "stations": stations
    }
    
    # Ensure directory exists
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Write the file
    OUTPUT_PATH.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"Catalog successfully written to {OUTPUT_PATH}.")

if __name__ == "__main__":
    main()
