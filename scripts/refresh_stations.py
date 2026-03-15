import json
import pathlib
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

BASE_URL = "https://api.weather.gov/stations"
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

        except urllib.error.URLError as exc:
            print(f"URL error while fetching {url}: {exc}", flush=True)
            last_error = exc

        except TimeoutError as exc:
            print(f"Timeout while fetching {url}: {exc}", flush=True)
            last_error = exc

        except json.JSONDecodeError as exc:
            print(f"Invalid JSON from {url}: {exc}", flush=True)
            last_error = exc

        except Exception as exc:
            print(f"Unexpected error while fetching {url}: {exc}", flush=True)
            last_error = exc

        if attempt < MAX_RETRIES:
            print(f"Retrying in {RETRY_DELAY_SECONDS} seconds...", flush=True)
            time.sleep(RETRY_DELAY_SECONDS)

    raise RuntimeError(f"Failed to fetch {url} after {MAX_RETRIES} attempts: {last_error}")


def get_next_url(payload: dict) -> str | None:
    pagination = payload.get("pagination")
    if isinstance(pagination, dict):
        next_url = pagination.get("next")
        if next_url:
            return next_url

    alt_pagination = payload.get("@pagination")
    if isinstance(alt_pagination, dict):
        next_url = alt_pagination.get("next")
        if next_url:
            return next_url

    return None


def parse_station(feature: dict) -> dict | None:
    properties = feature.get("properties", {})
    geometry = feature.get("geometry", {})

    station_id = properties.get("stationIdentifier")
    if not station_id:
        return None

    coordinates = geometry.get("coordinates", [None, None])
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
    url = BASE_URL
    page_number = 0
    stations = []
    seen_station_ids = set()

    while url:
        page_number += 1
        if page_number > 200:
            print("Stopping after 200 pages for safety.", flush=True)
        break

        payload = fetch_json(url)

        features = payload.get("features", [])
        print(f"Page {page_number}: found {len(features)} features", flush=True)
        # Stop if the API returns an empty page
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

        print(
            f"Added {added_this_page} new stations on page {page_number}. "
            f"Total stations so far: {len(stations)}",
            flush=True,
        )

        url = get_next_url(payload)

        if url:
            print("Moving to next page...", flush=True)
            time.sleep(PAGE_DELAY_SECONDS)

    return stations


def write_output(stations: list[dict]) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "National Weather Service API",
        "station_count": len(stations),
        "stations": stations,
    }

    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2),
        encoding="utf-8",
    )


def main() -> None:
    print("Refreshing full NWS station catalog...", flush=True)
    stations = get_all_stations()

    if not stations:
        raise RuntimeError("No stations were retrieved from the NWS API.")

    write_output(stations)

    print(f"Wrote {OUTPUT_PATH} with {len(stations)} stations.", flush=True)


if __name__ == "__main__":
    main()
