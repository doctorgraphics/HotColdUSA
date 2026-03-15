import json
import pathlib
import urllib.request
from datetime import datetime, timezone

BASE = "https://api.weather.gov"
USER_AGENT = "HotColdUSA/0.1 (https://github.com/doctorgraphics/HotColdUSA)"
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "application/geo+json",
}

OUTPUT_PATH = pathlib.Path("data/stations.json")


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_all_stations() -> list[dict]:
    url = f"{BASE}/stations"
    stations = []

    while url:
        payload = fetch_json(url)
        features = payload.get("features", [])

        for feature in features:
            props = feature.get("properties", {})
            geometry = feature.get("geometry", {})
            coords = geometry.get("coordinates", [None, None])

            station_id = props.get("stationIdentifier")
            name = props.get("name")

            if not station_id:
                continue

            lon = coords[0] if len(coords) > 0 else None
            lat = coords[1] if len(coords) > 1 else None

            stations.append({
                "station": station_id,
                "name": name,
                "latitude": lat,
                "longitude": lon,
                "time_zone": props.get("timeZone"),
                "county": props.get("county"),
                "forecast": props.get("forecast"),
            })

        pagination = payload.get("pagination", {})
        url = pagination.get("next")

        print(f"Fetched page, total stations so far: {len(stations)}")

    return stations


def main():
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
