import json
import math
import pathlib
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

BASE = "https://api.weather.gov"
USER_AGENT = "HotColdUSA/0.1 (https://github.com/doctorgraphics/HotColdUSA)"
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "application/geo+json",
}

STATIONS_PATH = pathlib.Path("data/stations.json")
OUTPUT_PATH = pathlib.Path("data/latest.json")

REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 3
REQUEST_DELAY_SECONDS = 0.1
BATCH_SIZE = 500

def c_to_f(celsius):
    if celsius is None: return None
    return (celsius * 9 / 5) + 32

def fetch_json(url: str) -> dict:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"Fetching: {url} (attempt {attempt}/{MAX_RETRIES})", flush=True)
            request = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            print(f"Error fetching {url}: {exc}", flush=True)
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY_SECONDS)
    raise RuntimeError(f"Failed to fetch {url} after {MAX_RETRIES} attempts.")

def load_station_catalog() -> list[dict]:
    if not STATIONS_PATH.exists():
        raise FileNotFoundError("data/stations.json not found. Run scripts/refresh_stations.py first.")
    payload = json.loads(STATIONS_PATH.read_text(encoding="utf-8"))
    return payload.get("stations", [])

def choose_station_batch(stations: list[dict]) -> tuple[list[dict], int]:
    if not stations: return [], 0
    total = len(stations)
    hour_index = int(datetime.now(timezone.utc).timestamp() // 3600)
    start_index = (hour_index * BATCH_SIZE) % total
    end_index = start_index + BATCH_SIZE
    if end_index <= total:
        batch = stations[start_index:end_index]
    else:
        batch = stations[start_index:] + stations[: end_index - total]
    return batch, start_index

def parse_state_from_county(county_url: str) -> str | None:
    """Extracts state code from NWS county URL (e.g., .../counties/AZC013 -> AZ)"""
    if not county_url or "/counties/" not in county_url:
        return None
    try:
        # State abbreviation starts immediately after '/counties/'
        parts = county_url.split("/counties/")
        if len(parts) > 1:
            return parts[1][:2].upper()
    except:
        pass
    return None

def safe_get_latest_observation(station: dict):
    station_id = station["station"]
    url = f"{BASE}/stations/{station_id}/observations/latest"

    try:
        payload = fetch_json(url)
        props = payload.get("properties", {})
        
        temp_c = props.get("temperature", {}).get("value")
        if temp_c is None: return None
        
        temp_f = c_to_f(temp_c)
        if temp_f is None or math.isnan(temp_f): return None

        # Extract state from the station catalog or the observation's county metadata
        state = station.get("state") or parse_state_from_county(station.get("county"))

        return {
            "station": station_id,
            "city": station.get("name") or station_id,
            "state": state,
            "temp_f": round(temp_f, 1),
            "observed_at": props.get("timestamp"),
            "condition": props.get("textDescription") or "Unknown",
            "latitude": station.get("latitude"),
            "longitude": station.get("longitude"),
        }
    except Exception as exc:
        print(f"Skipping {station_id}: {exc}", flush=True)
        return None

def write_output(observations: list[dict], hottest: dict, coldest: dict, catalog_size: int):
    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "National Weather Service API (METAR/SYNOP)",
        "catalog_size": catalog_size,
        "station_count": len(observations),
        "hottest": hottest,
        "coldest": coldest,
        "spread_f": round(hottest["temp_f"] - coldest["temp_f"], 1),
        "top_hot": sorted(observations, key=lambda x: x["temp_f"], reverse=True)[:5],
        "top_cold": sorted(observations, key=lambda x: x["temp_f"])[:5],
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2), encoding="utf-8")

def main():
    print("Loading station catalog...", flush=True)
    catalog = load_station_catalog()
    if not catalog: raise RuntimeError("Station catalog is empty.")

    batch, start_idx = choose_station_batch(catalog)
    print(f"Checking batch of {len(batch)} stations...", flush=True)

    observations = []
    for idx, station in enumerate(batch, start=1):
        obs = safe_get_latest_observation(station)
        if obs: observations.append(obs)
        if idx % 50 == 0: print(f"Progress: {idx}/{len(batch)}", flush=True)
        time.sleep(REQUEST_DELAY_SECONDS)

    if not observations: raise RuntimeError("No valid observations found.")

    hottest = max(observations, key=lambda x: x["temp_f"])
    coldest = min(observations, key=lambda x: x["temp_f"])

    write_output(observations, hottest, coldest, len(catalog))
    print(f"Success! Hottest: {hottest['city']}, {hottest['state']} ({hottest['temp_f']}°F)")

if __name__ == "__main__":
    main()
