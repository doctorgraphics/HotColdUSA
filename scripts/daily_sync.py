import json
import pathlib
from datetime import datetime, timezone

# Paths
RECORDS_PATH = pathlib.Path("data/records.json")
LATEST_PATH = pathlib.Path("data/latest.json")

def main():
    print("Running Daily Climate Sync...")
    
    # 1. Load Records
    if not RECORDS_PATH.exists():
        print("Error: records.json not found")
        return
    records = json.loads(RECORDS_PATH.read_text())
    
    # 2. Get Today's Key (MM-DD)
    today_key = datetime.now(timezone.utc).strftime("%m-%d")
    today_record = records.get(today_key, {
        "high": "--", "high_location": "N/A", 
        "low": "--", "low_location": "N/A"
    })

    # 3. Load Latest.json
    if not LATEST_PATH.exists():
        # Create a skeleton if it doesn't exist yet
        data = {"generated_at": datetime.now(timezone.utc).isoformat()}
    else:
        data = json.loads(LATEST_PATH.read_text())

    # 4. Inject Daily Records
    data["daily_records"] = today_record
    
    # 5. Save back to data/latest.json
    LATEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    LATEST_PATH.write_text(json.dumps(data, indent=2))
    print(f"Daily records for {today_key} synced successfully.")

if __name__ == "__main__":
    main()
