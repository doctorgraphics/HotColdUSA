import json
import pathlib
import urllib.request
from datetime import datetime, timezone

# Constants
STATIONS_PATH = pathlib.Path("data/stations.json")
OUTPUT_PATH = pathlib.Path("data/latest.json")

# Open-Meteo settings (No API Key Required)
BASE_URL = "https://api.open-meteo.com/v1/forecast"
BATCH_SIZE = 500 # Open-Meteo supports up to 1000 per request

def load_station_catalog():
    if not STATIONS_PATH.exists():
        raise FileNotFoundError("data/stations.json not found.")
    payload = json.loads(STATIONS_PATH.read_text(encoding="utf-8"))
    return payload.get("stations", [])

def get_weather_batch(stations):
    """Fetches weather for all 500 stations in one single API call."""
    lats = [str(s["latitude"]) for s in stations]
    lons = [str(s["longitude"]) for s in stations]
    
    params = [
        f"latitude={','.join(lats)}",
        f"longitude={','.join(lons)}",
        "current=temperature_2m,weather_code", # 'weather_code' gives us the icon
        "temperature_unit=fahrenheit",
        "wind_speed_unit=mph",
        "precipitation_unit=inch",
        "timezone=auto"
    ]
    
    url = f"{BASE_URL}?{'&'.join(params)}"
    print(f"Fetching batch of {len(stations)} stations from Open-Meteo...", flush=True)
    
    try:
        request = urllib.request.Request(url)
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        print(f"Batch fetch failed: {e}")
        return None

def get_condition_text(code):
    """Translates WMO Weather Codes to human-readable text."""
    # Simplified WMO translation
    codes = {
        0: "Clear Sky", 1: "Mainly Clear", 2: "Partly Cloudy", 3: "Overcast",
        45: "Foggy", 48: "Depositing Rime Fog", 51: "Light Drizzle",
        61: "Slight Rain", 63: "Rain", 71: "Slight Snow", 95: "Thunderstorm"
    }
    return codes.get(code, "Cloudy")

def main():
    catalog = load_station_catalog()
    if not catalog: return

    # For the pilot, we'll take the first 500. 
    # Your choose_station_batch logic still works here too.
    batch = catalog[:BATCH_SIZE]
    
    results = get_weather_batch(batch)
    if not results: return

    observations = []
    # Open-Meteo returns a list of results if multiple lats are provided
    for i, res in enumerate(results if isinstance(results, list) else [results]):
        station = batch[i]
        current = res.get("current", {})
        
        observations.append({
            "station": station["station"],
            "city": station["name"],
            "state": station.get("county", "").split("/")[-1][:2].upper(), # Quick state parse
            "temp_f": round(current.get("temperature_2m"), 1),
            "condition": get_condition_text(current.get("weather_code")),
            "observed_at": current.get("time"),
            "latitude": station["latitude"],
            "longitude": station["longitude"]
        })

    # Extreme Values
    hottest = max(observations, key=lambda x: x["temp_f"])
    coldest = min(observations, key=lambda x: x["temp_f"])

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "Open-Meteo (Aggregated NOAA/DWD/ECMWF)",
        "station_count": len(observations),
        "hottest": hottest,
        "coldest": coldest,
        "spread_f": round(hottest["temp_f"] - coldest["temp_f"], 1),
        "top_hot": sorted(observations, key=lambda x: x["temp_f"], reverse=True)[:5],
        "top_cold": sorted(observations, key=lambda x: x["temp_f"])[:5],
    }
    
    OUTPUT_PATH.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"Success! Hottest: {hottest['city']} ({hottest['temp_f']}°F)")

if __name__ == "__main__":
    main()
