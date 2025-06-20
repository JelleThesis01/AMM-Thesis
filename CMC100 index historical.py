# I use this script to obtain the historical CMC 100 index data. You need to purchase an API before you can use this script.

import requests
import pandas as pd
import time
from datetime import datetime, timedelta, timezone

API_KEY = "#INSERT API KEY"
url = "https://pro-api.coinmarketcap.com/v3/index/cmc100-historical"
headers = {
    "Accepts": "application/json",
    "X-CMC_PRO_API_KEY": API_KEY
}

start_date = datetime(2023, 1, 1, tzinfo=timezone.utc)
now = datetime.now(timezone.utc)
all_data = []  

current_start = start_date
while True:
    time_start_iso = current_start.strftime("%Y-%m-%dT%H:%M:%SZ")
    params = {"time_start": time_start_iso, "interval": "daily", "count": 10}
    backoff = 1
    max_retries = 5
    while True:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            break  
        if response.status_code == 429:
            if backoff > max_retries:
                raise Exception("Rate limit exceeded, aborting after retries")
            time.sleep(2 ** backoff)  
            backoff += 1
            continue
        response.raise_for_status()  
    data = response.json()
    entries = data.get("data", [])
    if not entries:
        break  
    all_data.extend(entries)
    last_ts = entries[-1].get("update_time") or entries[-1].get("timestamp")
    print(f"Retrieved {len(entries)} records, last timestamp {last_ts}.")

    if len(entries) < params["count"]:
        break
    if not last_ts:
        break  
    if len(last_ts) == 10:
        last_dt = datetime.strptime(last_ts, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    else:
        last_dt = datetime.fromisoformat(last_ts.replace("Z", "+00:00"))
    next_start = last_dt + timedelta(seconds=1)
    if next_start >= now:
        break  
    current_start = next_start
    time.sleep(1)

print(f"Total records fetched: {len(all_data)}")

df = pd.json_normalize(all_data)
if "timestamp" in df.columns:
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)

excel_file = "cmc100_daily.xlsx"
df.to_excel(excel_file, index=False)
print(f"Data exported to {excel_file}.")
