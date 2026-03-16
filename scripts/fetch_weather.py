import json
import pathlib
import urllib.request
from datetime import datetime, timezone

# Define paths
STATIONS_PATH = pathlib.Path("data/stations.json")
OUTPUT_PATH = pathlib.Path("data/latest.json")

def main():
    if not STATIONS_PATH.exists():
        print(f"Error: {STATIONS_PATH} not found.")
        return

    # 1. Load the fixed catalog
    catalog = json.loads(STATIONS_PATH.read_text(encoding="utf-8"))["stations"]
    
    # 2. Build the Batch URL for Open-Meteo
    lats = ",".join(str(s["latitude"]) for s in catalog)
    lons = ",".join(str(s["longitude"]) for s in catalog)
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lats}&longitude={lons}&current=temperature_2m&temperature_unit=fahrenheit"
    
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            results = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"API Fetch Failed: {e}")
        return

    data_list = results if isinstance(results, list) else [results]
    
    # 3. Process observations
    observations = []
    for i, res in enumerate(data_list):
        city_info = catalog[i]
        curr = res.get("current", {})
        
        observations.append({
            "city": city_info["name"],
            "state": city_info["state"],
            "temp_f": round(curr.get("temperature_2m", 0), 1)
        })

    # 4. Sort for rankings
    observations.sort(key=lambda x: x["temp_f"], reverse=True)

    # 5. Save only the essentials
    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "top_5_hot": observations[:5],
        "top_5_cold": observations[-5:][::-1] # Reverse so coldest is #1
    }
    
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(output, indent=2), encoding="utf-8")
    
    print(f"Latest.json updated with Top 5 extremes.")

if __name__ == "__main__":
    main()
