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

# How many stations to check in one hourly run.
BATCH_SIZE = 500


def c_to_f(celsius):
    if celsius is None:
        return None
    return (celsius * 9 / 5) + 32


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


def load_station_catalog() -> list[dict]:
    if not STATIONS_PATH.exists():
        raise FileNotFoundError(
            "data/stations.json not found. Run scripts/refresh_stations.py first."
        )

    payload = json.loads(STATIONS_PATH.read_text(encoding="utf-8"))
    stations = payload.get("stations", [])

    if not isinstance(stations, list):
        raise ValueError("data/stations.json is invalid: 'stations' must be a list.")

    cleaned = []
    seen = set()

    for station in stations:
        station_id = station.get("station")
        if not station_id or station_id in seen:
            continue

        seen.add(station_id)
        cleaned.append(station)

    return cleaned


def choose_station_batch(stations: list[dict]) -> tuple[list[dict], int]:
    if not stations:
        return [], 0

    total = len(stations)

    now = datetime.now(timezone.utc)
    hour_index = int(now.timestamp() // 3600)

    start_index = (hour_index * BATCH_SIZE) % total
    end_index = start_index + BATCH_SIZE

    if end_index <= total:
        batch = stations[start_index:end_index]
    else:
        batch = stations[start_index:] + stations[: end_index - total]

    return batch, start_index


def safe_get_latest_observation(station: dict):
    station_id = station["station"]
    url = f"{BASE}/stations/{station_id}/observations/latest"

    try:
        payload = fetch_json(url)
        properties = payload.get("properties", {})
        geometry = payload.get("geometry", {})

        temperature = properties.get("temperature", {}).get("value")
        if temperature is None:
            return None

        temp_f = c_to_f(temperature)
        if temp_f is None or math.isnan(temp_f):
            return None

        coordinates = geometry.get("coordinates", [None, None])
        lon = coordinates[0] if len(coordinates) > 0 else station.get("longitude")
        lat = coordinates[1] if len(coordinates) > 1 else station.get("latitude")

        observation = {
            "station": station_id,
            "city": station.get("name") or station_id,
            "state": None,
            "temp_f": round(temp_f, 1),
            "observed_at": properties.get("timestamp"),
            "condition": properties.get("textDescription") or "Unknown",
            "lat": lat,
            "lon": lon,
        }

        return observation

    except Exception as exc:
        print(f"Skipping {station_id}: {exc}", flush=True)
        return None


def filter_extreme_candidates(observations: list[dict]) -> list[dict]:
    filtered = []

    for obs in observations:
        temp_f = obs.get("temp_f")
        observed_at = obs.get("observed_at")

        if temp_f is None:
            continue

        # Loose sanity bounds for U.S. surface observations.
        if temp_f < -100 or temp_f > 150:
            continue

        if not observed_at:
            continue

        filtered.append(obs)

    return filtered


def write_output(
    observations: list[dict],
    hottest: dict,
    coldest: dict,
    batch_start_index: int,
    stations_checked: int,
    catalog_size: int,
):
    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "National Weather Service API",
        "catalog_size": catalog_size,
        "stations_checked": stations_checked,
        "batch_start_index": batch_start_index,
        "station_count": len(observations),
        "hottest": hottest,
        "coldest": coldest,
        "spread_f": round(hottest["temp_f"] - coldest["temp_f"], 1),
        "top_hot": sorted(observations, key=lambda x: x["temp_f"], reverse=True)[:5],
        "top_cold": sorted(observations, key=lambda x: x["temp_f"])[:5],
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(output, indent=2), encoding="utf-8")


def main():
    print("Loading station catalog...", flush=True)
    station_catalog = load_station_catalog()

    if not station_catalog:
        raise RuntimeError("Station catalog is empty.")

    batch, batch_start_index = choose_station_batch(station_catalog)

    print(
        f"Catalog size: {len(station_catalog)} stations | "
        f"Checking batch of {len(batch)} starting at index {batch_start_index}",
        flush=True,
    )

    observations = []

    for idx, station in enumerate(batch, start=1):
        observation = safe_get_latest_observation(station)
        if observation is not None:
            observations.append(observation)

        if idx % 25 == 0:
            print(
                f"Checked {idx}/{len(batch)} stations | "
                f"Valid observations so far: {len(observations)}",
                flush=True,
            )

        time.sleep(REQUEST_DELAY_SECONDS)

    observations = filter_extreme_candidates(observations)

    if not observations:
        raise RuntimeError("No usable station observations were retrieved.")

    hottest = max(observations, key=lambda x: x["temp_f"])
    coldest = min(observations, key=lambda x: x["temp_f"])

    write_output(
        observations=observations,
        hottest=hottest,
        coldest=coldest,
        batch_start_index=batch_start_index,
        stations_checked=len(batch),
        catalog_size=len(station_catalog),
    )

    print(f"Wrote {OUTPUT_PATH}", flush=True)
    print(f"Hottest: {hottest['city']} {hottest['temp_f']}°F", flush=True)
    print(f"Coldest: {coldest['city']} {coldest['temp_f']}°F", flush=True)


if __name__ == "__main__":
    main()
