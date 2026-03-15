import json
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

OUTPUT_PATH = pathlib.Path("data/stations.json")
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 5


def fetch_json(url: str) -> dict:
    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"Fetching: {url} (attempt {attempt}/{MAX_RETRIES})")
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8"))

        except urllib.error.HTTPError as exc:
            body = ""
            try:
                body = exc.read().decode("utf-8", errors="replace")
            except Exception:
                pass
            print(f"HTTP error {exc.code} for {url}")
            if body:
                print(body[:1000])
            last_error = exc

        except Exception as exc:
            print(f"Request failed for {url}: {exc}")
            last_error = exc

        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY_SECONDS)

    raise RuntimeError(f"Failed to fetch {url}: {last_error}")


def get_next_url(payload: dict):
    pagination = payload.get("pagination", {})
    if isinstance(pagination, dict) and pagination.get("next"):
        return pagination["next"]

    alt_pagination = payload.get("@pagination", {})
    if isinstance(alt_pagination, dict) and alt_pagination.get("next"):
        return alt_pagination["next"]

    return None


def get_all_stations() -> list[dict]:
    url = f"{BASE}/stations"
    stations = []
    seen = set()
    page_num = 0

    while url:
        page_num += 1
        payload = fetch_json(url)
        features = payload.get("features", [])
        print(f"Page {page_num}: {len(features)} stations")

        for feature in features:
            props = feature.get("properties", {})
            geometry = feature.get("geometry", {})
            coords = geometry.get("coordinates", [None, None])

            station_id = props.get("stationIdentifier")
            if not station_id or station_id in seen:
                continue

            seen.add(station_id)

            lon = coords[0] if len(coords) > 0 else None
            lat = coords[1] if len(coords) > 1 else None

            stations.append({
                "station": station_id,
                "name": props.get("name"),
                "latitude": lat,
                "longitude": lon,
                "time_zone": props.get("timeZone"),
                "county": props.get("county"),
                "forecast": props.get("forecast"),
            })

        url = get_next_url(payload)
        print(f"Total stations so far: {len(stations)}")
        time.sleep(0.5)

    return stations


def main():
    print("Refreshing full NWS station catalog...")
    stations = get_all_stations()

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "National Weather Service API",
        "station_count": len(stations),
        "stations": stations,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(output, indent=2), encoding="utf-8")

    print(f"Wrote {OUTPUT_PATH} with {len(stations)} stations.")


if __name__ == "__main__":
    main()
