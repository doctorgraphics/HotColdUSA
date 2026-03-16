import json
import pathlib
import urllib.request
from datetime import datetime, timezone

# Define paths
STATIONS_PATH = pathlib.Path("data/stations.json")
OUTPUT_PATH = pathlib.Path("data/latest.json")

def get_condition_text(code):
    """Translates WMO Weather Codes from Open-Meteo to human-readable text."""
    mapping = {
        0: "Clear Sky", 1: "Mainly Clear", 2: "Partly Cloudy", 3: "Overcast",
        45: "Foggy", 48: "Rime Fog", 51: "Light Drizzle", 53: "Drizzle",
        61: "Slight Rain", 63: "Rain", 71: "Slight Snow", 73: "Snow",
        80: "Rain Showers", 95: "Thunderstorm"
    }
    return mapping.get(code, "Cloudy")

def main():
    print("Loading city catalog...", flush=True)
    if not STATIONS_PATH.exists():
        print(f"Error: {STATIONS_PATH} not found.")
        return

    catalog = json.loads(STATIONS_PATH.read_text(encoding="utf-8"))["stations"]
    
    # 1. Build the Batch URL
    lats = ",".join(str(s["latitude"]) for s in catalog)
    lons = ",".join(str(s["longitude"]) for s in catalog)
    
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lats}&longitude={lons}&current=temperature_2m,weather_code"
        f"&temperature_unit=fahrenheit&timezone=auto"
    )
    
    print(f"Fetching weather for {len(catalog)} cities from Open-Meteo...", flush=True)
    
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            results = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"API Fetch Failed: {e}")
        return

    # Open-Meteo returns a list if multiple lats were provided
    data_list = results if isinstance(results, list) else [results]
    
    observations = []
    by_state = {}

    for i, res in enumerate(data_list):
        city_info = catalog[i]
        curr = res.get("current", {})
        
        obs = {
            "city": city_info["name"],
            "state": city_info["state"],
            "temp_f": round(curr.get("temperature_2m", 0), 1),
            "condition": get_condition_text(curr.get("weather_code")),
            "observed_at": curr.get("time"),
            "latitude": city_info["latitude"],
            "longitude": city_info["longitude"]
        }
        observations.append(obs)
        by_state[city_info["state"]] = obs

    # 2. Rank and Group
    observations.sort(key=lambda x: x["temp_f"], reverse=True)

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "Open-Meteo",
        "hottest": observations[0],
        "coldest": observations[-1],
        "top_5_hot": observations[:5],
        "top_5_cold": observations[-5:][::-1],
        "by_state": by_state
    }
    
    # 3. Save to data/latest.json
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"Success! Hottest: {output['hottest']['city']} ({output['hottest']['temp_f']}°F)")

if __name__ == "__main__":
    main()
