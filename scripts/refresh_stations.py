import json
import pathlib
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

# Constants for the National Weather Service API
BASE_URL = "https://api.weather.gov/stations"
USER_AGENT = "HotColdUSA/0.1 (https://github.com/doctorgraphics/HotColdUSA)"
OUTPUT_PATH = pathlib.Path("data/stations.json")

HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "application/geo+json",
}

# Configuration for reliability and rate limiting
REQUEST_TIMEOUT = 60
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 5
PAGE_DELAY_SECONDS = 0.5
MAX_PAGES = 500  # Safety limit to prevent infinite loops


def fetch_json(url: str) -> dict:
    """Fetches JSON data from a URL with retry logic."""
    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"Fetching: {url} (attempt {attempt}/{MAX_RETRIES})", flush=True)

            request = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
                body = response.read().decode("utf-8")
                return json.loads(body)

        except urllib.error.HTTPError as exc:
            error_body = ""
            try:
                error_body = exc.read().decode("utf-8", errors="replace")
            except Exception:
                pass

            print(f"HTTP error {exc.code} while fetching {url}", flush=True)
            if error_body:
                print(error_body[:1000], flush=True)
            last_error = exc

        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, Exception) as exc:
            print(f"Error while fetching {url}: {exc}", flush=True)
            last_error = exc

        if attempt < MAX_RETRIES:
            print(f"Retrying in {RETRY_DELAY_SECONDS} seconds...", flush=True)
            time.sleep(RETRY_DELAY_SECONDS)

    raise RuntimeError(f"Failed to fetch {url} after {MAX_RETRIES} attempts: {last_error}")


def get_next_url(payload: dict) -> str | None:
    """Extracts the 'next' page URL from the API response pagination."""
    for key in ["pagination", "@pagination"]:
        pagination = payload.get(key)
        if isinstance(pagination, dict):
            next_url = pagination.get("next")
            if next_url:
                return next_url
    return None


def parse_station(feature: dict) -> dict | None:
    """Extracts relevant station metadata from a GeoJSON feature."""
    properties = feature.get("properties", {})
    geometry = feature.get("geometry", {})

    station_id = properties.get("stationIdentifier")
    if not station_id:
        return None

    coordinates = geometry.get("coordinates", [None, None])
    # GeoJSON coordinates are [longitude, latitude]
    longitude = coordinates[0] if len(coordinates) > 0 else None
    latitude = coordinates[1] if len(coordinates) > 1 else None

    return {
        "station": station_id,
        "name": properties.get("name"),
        "latitude": latitude,
        "longitude": longitude,
        "time_zone": properties.get("timeZone"),
        "county": properties.get("county"),
        "forecast": properties.get("forecast"),
    }


def get_all_stations() -> list[dict]:
    """Iterates through all pages of the NWS API to collect every weather station."""
    url = BASE_URL
    page_number = 0
    stations = []
    seen_station_ids = set()

    while url:
        page_number += 1
        if page_number > MAX_PAGES:
            print(f"Reached safety limit of {MAX_PAGES} pages. Stopping.", flush=True)
            break

        payload = fetch_json(url)
        features = payload.get("features", [])
        
        if not features:
            print("No features returned. Ending pagination.", flush=True)
            break

        added_this_page = 0
        for feature in features:
            station = parse_station(feature)
            if not station:
                continue

            station_id = station["station"]
            if station_id in seen_station_ids:
                continue

            seen_station_ids.add(station_id)
            stations.append(station)
            added_this_page += 1

        print(f"Page {page_number}: Added {added_this_page} new stations. Total: {len(stations)}", flush=True)

        url = get_next_url(payload)
        if url:
            time.sleep(PAGE_DELAY_SECONDS)

    return stations


def write_output(stations: list[dict]) -> None:
    """Saves the collected station list to the data directory."""
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "National Weather Service API",
        "station_count": len(stations),
        "stations": stations,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2), encoding="utf-8")


def main() -> None:
    """Main execution flow for refreshing the station catalog."""
    print("Refreshing full NWS station catalog...", flush=True)
    try:
        stations = get_all_stations()
        if not stations:
            raise RuntimeError("No stations were retrieved from the NWS API.")

        write_output(stations)
        print(f"Successfully wrote {OUTPUT_PATH} with {len(stations)} stations.", flush=True)
    except Exception as e:
        print(f"Failed to refresh stations: {e}", flush=True)
        exit(1)


if __name__ == "__main__":
    main()
