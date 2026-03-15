import json
import pathlib
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

# Constants for filtering
US_AREAS = [
    "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA","KS","KY","LA","ME","MD",
    "MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH","OK","OR","PA","RI","SC",
    "SD","TN","TX","UT","VT","VA","WA","WV","WI","WY","DC","AS","GU","MP","PR","VI"
]

USER_AGENT = "HotColdUSA/0.1 (https://github.com/doctorgraphics/HotColdUSA)"
OUTPUT_PATH = pathlib.Path("data/stations.json")

HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "application/geo+json",
}

REQUEST_TIMEOUT = 60
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 5
PAGE_DELAY_SECONDS = 0.5

def fetch_json(url: str) -> dict:
    """Fetches JSON data from a URL with retry logic."""
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

def get_next_url(payload: dict) -> str | None:
    """Extracts and cleans the pagination link from the NWS API."""
    for key in ["pagination", "@pagination"]:
        page = payload.get(key)
        if isinstance(page, dict):
            next_url = page.get("next")
            if next_url:
                # FIX: The NWS API mangles 'state=AK' into 'state%5B0%5D=AK' 
                # in its own pagination links. This line fixes it.
                return next_url.replace("state%5B0%5D=", "state=")
    return None

def parse_station(feature: dict) -> dict | None:
    """Filters for 4-character METAR/ICAO identifiers."""
    properties = feature.get("properties", {})
    station_id = properties.get("stationIdentifier")
    
    # Only keep professional airport stations (4 chars)
    if not station_id or len(station_id) != 4:
        return None

    coords = feature.get("geometry", {}).get("coordinates", [None, None])
    return {
        "station": station_id,
        "name": properties.get("name"),
        "latitude": coords[1] if len(coords) > 1 else None,
        "longitude": coords[0] if len(coords) > 0 else None,
        "time_zone": properties.get("timeZone"),
    }

def get_all_stations() -> list[dict]:
    """Fetches stations state-by-state to ensure reliability and speed."""
    stations = []
    seen = set()

    for area in US_AREAS:
        print(f"--- Processing {area} ---", flush=True)
        url = f"https://api.weather.gov/stations?state={area}&limit=500"
        
        while url:
            payload = fetch_json(url)
            features = payload.get("features", [])
            
            if not features:
                break

            added_this_area = 0
            for f in features:
                station = parse_station(f)
                if station and station["station"] not in seen:
                    seen.add(station["station"])
                    stations.append(station)
                    added_this_area += 1

            print(f"  {area}: Added {added_this_area} stations. Total: {len(stations)}", flush=True)
            url = get_next_url(payload)
            if url:
                time.sleep(PAGE_DELAY_SECONDS)

    return stations

def main():
    print("Refreshing US METAR station catalog...", flush=True)
    try:
        stations = get_all_stations()
        if not stations:
            raise RuntimeError("No stations found.")

        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        output = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source": "National Weather Service API (METAR/SYNOP)",
            "station_count": len(stations),
            "stations": stations,
        }
        OUTPUT_PATH.write_text(json.dumps(output, indent=2), encoding="utf-8")
        print(f"Successfully wrote {len(stations)} stations to {OUTPUT_PATH}.", flush=True)
    except Exception as e:
        print(f"Refresh failed: {e}", flush=True)
        exit(1)

if __name__ == "__main__":
    main()
