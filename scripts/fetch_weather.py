import json
import pathlib
import urllib.request
from datetime import datetime, timezone

STATIONS_PATH = pathlib.Path("data/stations.json")
OUTPUT_PATH = pathlib.Path("data/latest.json")

def get_condition_text(code):
    # WMO Weather interpretation codes
    mapping = {
        0: "Clear Sky", 1: "Mainly Clear", 2: "Partly Cloudy", 3: "Overcast",
        45: "Foggy", 51: "Drizzle", 61: "Rain", 71: "Snow", 95: "Thunderstorm"
    }
    return mapping.get(code, "Cloudy")

def main():
    if not STATIONS_PATH.exists(): return
    catalog = json.loads(STATIONS_PATH.read_text())["stations"]
    
    # Batch coordinates
    lats = ",".join(str(s["latitude"]) for s in catalog)
    lons = ",".join(str(s["longitude"]) for s in catalog)
    
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lats}&longitude={lons}&current=temperature_2m,weather_code&temperature_unit=fahrenheit"
    
    print(f"Fetching weather for {len(catalog)} cities...")
    with urllib.request.urlopen(url) as resp:
        results = json.loads(resp.read().decode())
    
    data_list = results if isinstance(results, list) else [results]
    
    observations = []
    by_state = {}

    for i, res in enumerate(data_list):
        city_data = catalog[i]
        curr = res.get("current", {})
        
        obs = {
            "city": city_data["name"],
            "state": city_data["state"],
            "temp_f": round(curr.get("temperature_2m", 0), 1),
            "condition": get_condition_text(curr.get("weather_code")),
            "observed_at": curr.get("time")
        }
        observations.append(obs)
        by_state[city_data["state"]] = obs

    # Sort for Hottest/Coldest rankings
    observations.sort(key=lambda x: x["temp_f"], reverse=True)

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "hottest": observations[0],
        "coldest": observations[-1],
        "top_5_hot": observations[:5],
        "top_5_cold": observations[-5:][::-1],
        "by_state": by_state
    }
    
    OUTPUT_PATH.write_text(json.dumps(output, indent=2))
    print("latest.json updated.")

if __name__ == "__main__":
    main()
