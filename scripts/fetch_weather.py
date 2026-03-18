import json
import pathlib
import urllib.request
from datetime import datetime, timezone

# Define paths
STATIONS_PATH = pathlib.Path("data/stations.json")
RECORDS_PATH = pathlib.Path("data/records.json")
OUTPUT_PATH = pathlib.Path("data/latest.json")

def main():
    if not STATIONS_PATH.exists():
        print(f"Error: {STATIONS_PATH} not found.")
        return

    # 1. Load the fixed catalog
    stations_data = json.loads(STATIONS_PATH.read_text(encoding="utf-8"))
    catalog = stations_data["stations"]
    
    # 2. Build the Batch URL for Open-Meteo
    lats = ",".join(str(s["latitude"]) for s in catalog)
    lons = ",".join(str(s["longitude"]) for s in catalog)
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lats}&longitude={lons}&current=temperature_2m&temperature_unit=fahrenheit"
    
    try:
        print("Fetching live weather data...")
        with urllib.request.urlopen(url, timeout=30) as resp:
            results = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"API Fetch Failed: {e}")
        return

    # Open-Meteo returns a list if multiple locations are requested
    data_list = results if isinstance(results, list) else [results]
    
    # 3. Process observations including coordinates for the WarGames Map
    observations = []
    for i, res in enumerate(data_list):
        city_info = catalog[i]
        curr = res.get("current", {})
        
        observations.append({
            "city": city_info["name"],
            "state": city_info["state"],
            "temp_f": round(curr.get("temperature_2m", 0), 1),
            "lat": city_info["latitude"],
            "lon": city_info["longitude"]
        })

    # 4. Sort for rankings (Hottest first)
    observations.sort(key=lambda x: x["temp_f"], reverse=True)

    # 5. Load Historical Records for Today
    today_key = datetime.now(timezone.utc).strftime("%m-%d")
    daily_record = {"high": "--", "high_location": "N/A", "low": "--", "low_location": "N/A"}
    
    if RECORDS_PATH.exists():
        try:
            records_data = json.loads(RECORDS_PATH.read_text(encoding="utf-8"))
            daily_record = records_data.get(today_key, daily_record)
        except Exception as e:
            print(f"Could not read records: {e}")

    # 6. Build the Final Output Dictionary
    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "top_5_hot": observations[:5],
        "top_5_cold": observations[-5:][::-1], # Reverse so the coldest is index [0]
        "daily_records": daily_record,
        "source": "Open-Meteo / WOPR Tactical"
    }
    
    # 7. Save to latest.json
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(output, indent=2), encoding="utf-8")
    
    print(f"Mission Accomplished: latest.json updated with weather and records.")

if __name__ == "__main__":
    main()
