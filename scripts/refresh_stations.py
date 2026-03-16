OUTPUT_PATH = pathlib.Path("data/stations.json")

# Generic city list grouped by state
CITIES = [
    {"city": "Montgomery", "state": "AL", "lat": 32.377, "lon": -86.300},
    {"city": "Juneau", "state": "AK", "lat": 58.301, "lon": -134.420},
    {"city": "Phoenix", "state": "AZ", "lat": 33.448, "lon": -112.074},
    {"city": "Sacramento", "state": "CA", "lat": 38.576, "lon": -121.493},
    {"city": "Denver", "state": "CO", "lat": 39.739, "lon": -104.990},
    {"city": "Bismarck", "state": "ND", "lat": 46.808, "lon": -100.783},
    {"city": "Little Rock", "state": "AR", "lat": 34.746, "lon": -92.289},
    {"city": "Hartford", "state": "CT", "lat": 41.764, "lon": -72.682},
    {"city": "Dover", "state": "DE", "lat": 39.158, "lon": -75.524},
    {"city": "Tallahassee", "state": "FL", "lat": 30.438, "lon": -84.281},
    {"city": "Atlanta", "state": "GA", "lat": 33.749, "lon": -84.388},
    {"city": "Honolulu", "state": "HI", "lat": 21.307, "lon": -157.858},
    {"city": "Boise", "state": "ID", "lat": 43.615, "lon": -116.202},
    {"city": "Springfield", "state": "IL", "lat": 39.799, "lon": -89.644},
    {"city": "Indianapolis", "state": "IN", "lat": 39.768, "lon": -86.158},
    {"city": "Des Moines", "state": "IA", "lat": 41.586, "lon": -93.625},
    {"city": "Topeka", "state": "KS", "lat": 39.047, "lon": -95.675},
    {"city": "Frankfort", "state": "KY", "lat": 38.200, "lon": -84.873},
    {"city": "Baton Rouge", "state": "LA", "lat": 30.451, "lon": -91.187},
    {"city": "Augusta", "state": "ME", "lat": 44.310, "lon": -69.779},
    {"city": "Annapolis", "state": "MD", "lat": 38.978, "lon": -76.492},
    {"city": "Boston", "state": "MA", "lat": 42.360, "lon": -71.058},
    {"city": "Lansing", "state": "MI", "lat": 42.732, "lon": -84.555},
    {"city": "Saint Paul", "state": "MN", "lat": 44.953, "lon": -93.090},
    {"city": "Jackson", "state": "MS", "lat": 32.299, "lon": -90.184},
    {"city": "Jefferson City", "state": "MO", "lat": 38.576, "lon": -92.173},
    {"city": "Helena", "state": "MT", "lat": 46.589, "lon": -112.039},
    {"city": "Lincoln", "state": "NE", "lat": 40.813, "lon": -96.702},
    {"city": "Carson City", "state": "NV", "lat": 39.163, "lon": -119.767},
    {"city": "Concord", "state": "NH", "lat": 43.208, "lon": -71.538},
    {"city": "Trenton", "state": "NJ", "lat": 40.217, "lon": -74.743},
    {"city": "Santa Fe", "state": "NM", "lat": 35.687, "lon": -105.938},
    {"city": "Albany", "state": "NY", "lat": 42.652, "lon": -73.756},
    {"city": "Raleigh", "state": "NC", "lat": 35.780, "lon": -78.639},
    {"city": "Columbus", "state": "OH", "lat": 39.961, "lon": -82.999},
    {"city": "Oklahoma City", "state": "OK", "lat": 35.467, "lon": -97.516},
    {"city": "Salem", "state": "OR", "lat": 44.942, "lon": -123.035},
    {"city": "Harrisburg", "state": "PA", "lat": 40.273, "lon": -76.886},
    {"city": "Providence", "state": "RI", "lat": 41.824, "lon": -71.412},
    {"city": "Columbia", "state": "SC", "lat": 34.000, "lon": -81.035},
    {"city": "Pierre", "state": "SD", "lat": 44.368, "lon": -100.351},
    {"city": "Nashville", "state": "TN", "lat": 36.162, "lon": -86.781},
    {"city": "Austin", "state": "TX", "lat": 30.267, "lon": -97.743},
    {"city": "Salt Lake City", "state": "UT", "lat": 40.760, "lon": -111.891},
    {"city": "Montpelier", "state": "VT", "lat": 44.260, "lon": -72.575},
    {"city": "Richmond", "state": "VA", "lat": 37.540, "lon": -77.436},
    {"city": "Olympia", "state": "WA", "lat": 47.037, "lon": -122.900},
    {"city": "Charleston", "state": "WV", "lat": 38.349, "lon": -81.633},
    {"city": "Madison", "state": "WI", "lat": 43.073, "lon": -89.401},
    {"city": "Cheyenne", "state": "WY", "lat": 41.140, "lon": -104.820}
]

def main():
    print("Generating city catalog...")
    
    stations = []
    for city in CITIES:
        stations.append({
            "station": f"{city['state']}_{city['name'].replace(' ', '')}",
            "name": city['name'],
            "state": city['state'],
            "latitude": city['lat'],
            "longitude": city['lon']
        })

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "description": "50 US Cities (One per State)",
        "stations": stations
    }
    
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(output, indent=2))
    print(f"Catalog created with {len(stations)} cities.")

if __name__ == "__main__":
    main()
