import json
import pathlib
from datetime import datetime, timezone

# Paths
RECORDS_PATH = pathlib.Path("data/records.json")
LATEST_PATH = pathlib.Path("data/latest.json")

def main():
    print("🚀 Starting Daily Climate Sync...")
    
    # 1. Load the master records
    if not RECORDS_PATH.exists():
        print("❌ Error: records.json not found in data/ folder")
        return
    records = json.loads(RECORDS_PATH.read_text())
    
    # 2. Get Today's Key (MM-DD)
    today_key = datetime.now(timezone.utc).strftime("%m-%d")
    today_record = records.get(today_key, {
        "high": "--", "high_location": "N/A", 
        "low": "--", "low_location": "N/A"
    })

    # 3. Load latest.json from the runner (copied from data-storage branch)
    if not LATEST_PATH.exists():
        print("⚠️ latest.json not found. Creating a new one...")
        data = {"generated_at": datetime.now(timezone.utc).isoformat()}
    else:
        data = json.loads(LATEST_PATH.read_text())

    # 4. Inject Daily Records
    data["record_key"] = today_key
    data["daily_records"] = today_record
    
    # 5. Write it back
    LATEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    LATEST_PATH.write_text(json.dumps(data, indent=2))
    print(f"✅ Success! Daily records for {today_key} are now in latest.json.")

if __name__ == "__main__":
    main()
