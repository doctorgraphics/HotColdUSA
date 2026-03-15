# scripts/fetch_weather.py
import json
import math
import pathlib
import urllib.request
from datetime import datetime, timezone

BASE = "https://api.weather.gov"
USER_AGENT = "HotColdUSA/0.1 (https://github.com/doctorgraphics/HotColdUSA)"
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "application/geo+json",
}

# Starter station list for proof of concept.
# You can expand this later or replace it with a bigger curated list.
STATIONS = [
    "KPHX",   # Phoenix
    "KNYL",   # Yuma
    "KIPL",   # Imperial
    "KPSP",   # Palm Springs
    "KLAS",   # Las Vegas
    "KABQ",   # Albuquerque
    "KDEN",   # Denver
    "KMSP",   # Minneapolis
    "KINL",   # International Falls
    "KDLH",   # Duluth
    "KJFK",   # New York
    "KBOS",   # Boston
    "KSEA",   # Seattle
    "KPDX",   # Portland
    "KORD",   # Chicago
    "KATL",   # Atlanta
    "KMIA",   # Miami
    "KFAI",   # Fairbanks
    "PANC",   # Anchorage
]

def c_to_f(celsius):
    if celsius is None:
        return None
    return (celsius * 9 / 5) + 32

def fetch_json(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))

def safe_get_latest_observation(station_id):
    url = f"{BASE}/stations/{station_id}/observations/latest"
    try:
        payload = fetch_json(url)
        props = payload.get("properties", {})
        temp_c = props.get("temperature", {}).get("value")
        if temp_c is None:
            return None

        temp_f = c_to_f(temp_c)
        name = props.get("textDescription") or "Unknown"
        timestamp = props.get("timestamp")

        geometry = payload.get("geometry", {})
        coords = geometry.get("coordinates", [None, None])
        lon = coords[0] if len(coords) > 0 else None
        lat = coords[1] if len(coords) > 1 else None

        # Station metadata is not always fully present in latest obs, so fetch station info too.
        station_meta = fetch_json(f"{BASE}/stations/{station_id}")
        sprops = station_meta.get("properties", {})

        return {
            "station": station_id,
            "city": sprops.get("name", station_id),
            "state": None,  # NWS station endpoint doesn't always give state cleanly
            "temp_f": round(temp_f, 1),
            "observed_at": timestamp,
            "condition": name,
            "lat": lat,
            "lon": lon,
        }
    except Exception:
        return None

def main():
    observations = []

    for station_id in STATIONS:
        obs = safe_get_latest_observation(station_id)
        if obs is not None and not math.isnan(obs["temp_f"]):
            observations.append(obs)

    if not observations:
        raise RuntimeError("No station observations were retrieved.")

    hottest = max(observations, key=lambda x: x["temp_f"])
    coldest = min(observations, key=lambda x: x["temp_f"])

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "National Weather Service API",
        "station_count": len(observations),
        "hottest": hottest,
        "coldest": coldest,
        "spread_f": round(hottest["temp_f"] - coldest["temp_f"], 1),
        "top_hot": sorted(observations, key=lambda x: x["temp_f"], reverse=True)[:5],
        "top_cold": sorted(observations, key=lambda x: x["temp_f"])[:5],
    }

    out_path = pathlib.Path("data/latest.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")

if __name__ == "__main__":
    main()
