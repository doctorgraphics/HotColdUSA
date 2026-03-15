import json
import pathlib
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

# List of all 50 US states, DC, and territories
US_AREAS = ["AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA","KS","KY","LA","ME","MD",
            "MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH","OK","OR","PA","RI","SC",
            "SD","TN","TX","UT","VT","VA","WA","WV","WI","WY","DC","AS","GU","MP","PR","VI"]

# Create a single string like "AL,AK,AZ..."
state_string = ",".join(US_AREAS)
BASE_URL = f"https://api.weather.gov/stations?state={state_string}"

# Adding the state parameter filters the API results to the US only
BASE_URL = f"https://api.weather.gov/stations?state={','.join(US_AREAS)}"
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
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"Fetching: {url} (attempt {attempt}/{MAX_RETRIES})", flush=True)
            request = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            print(f"Error fetching {url}: {exc}", flush=True)
            last_error = exc
        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY_SECONDS)
    raise RuntimeError(f"Failed to fetch {url}: {last_error}")

def get_next_url(payload: dict) -> str | None:
    for key in ["pagination", "@pagination"]:
        page = payload.get(key)
        if isinstance(page, dict) and page.get("next"):
            return page.get("next")
    return None

def parse_station(feature: dict) -> dict | None:
    properties = feature.get("properties", {})
    station_id = properties.get("stationIdentifier")
    
    # METAR/SYNOP stations strictly use 4-character identifiers (ICAO codes)
    if not station_id or len(station_id) != 4:
        return None

    geometry = feature.get("geometry", {})
    coords = geometry.get("coordinates", [None, None])

    return {
        "station": station_id,
        "name": properties.get("name"),
        "latitude": coords[1] if len(coords) > 1 else None,
        "longitude": coords[0] if len(coords) > 0 else None,
        "time_zone": properties.get("timeZone"),
    }

def get_all_stations() -> list[dict]:
    url = BASE_URL
    stations = []
    seen = set()
    page = 0

    while url:
        page += 1
        payload = fetch_json(url)
        features = payload.get("features", [])
        
        if not features:
            break

        added_this_page = 0
        for f in features:
            station = parse_station(f)
            if station and station["station"] not in seen:
                seen.add(station["station"])
                stations.append(station)
                added_this_page += 1

        print(f"Page {page}: Added {added_this_page} METAR stations. Total: {len(stations)}", flush=True)
        url = get_next_url(payload)
        if url:
            time.sleep(PAGE_DELAY_SECONDS)

    return stations

def main():
    print("Refreshing US METAR/SYNOP station catalog...", flush=True)
    stations = get_all_stations()
    
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "National Weather Service API (METAR/SYNOP)",
        "station_count": len(stations),
        "stations": stations,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"Wrote {len(stations)} stations to {OUTPUT_PATH}.", flush=True)

if __name__ == "__main__":
    main()
