# I used this script to obtain daily data from a Uniswap v3 pool. Daily data can be anything specified under query. To use this script you would need to insert your own API key and specify the timestamp. 

import requests
import pandas as pd
import json
import os

API_KEY = "#INSTER API KEY"
SUBGRAPH_ID = "EYCKATKGBKLWvSfwvBjzfCBmGwYNdVkduYXVivCsLRFu"
POOL_ADDRESS = "0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc".lower()  
START_TIMESTAMP = #Timestamp      
END_TIMESTAMP = #Timestamp        
CHECKPOINT_FILE = "last_timestamp2.json"
OUTPUT_EXCEL = "UniswapV2_USDC-ETH.xlsx"
url = f"https://gateway.thegraph.com/api/{API_KEY}/subgraphs/id/{SUBGRAPH_ID}"
if os.path.exists(CHECKPOINT_FILE):
    with open(CHECKPOINT_FILE, "r") as f:
        data = json.load(f)
        last_fetched_timestamp = data.get("last_timestamp", START_TIMESTAMP)
        start_timestamp = last_fetched_timestamp + 1
else:
    start_timestamp = START_TIMESTAMP

all_records = []  

while True:
    query = f"""
    query {{
      pairDayDatas(
        first: 1000,
        orderBy: date,
        orderDirection: asc,
        where: {{
          pairAddress: "{POOL_ADDRESS}",
          date_gte: {start_timestamp},
          date_lte: {END_TIMESTAMP}
        }}
      ) {{
        date
        pairAddress
        reserve0
        reserve1
        totalSupply
        reserveUSD
        dailyVolumeToken0
        dailyVolumeToken1
        dailyVolumeUSD
        dailyTxns
      }}
    }}
    """
    try:
        response = requests.post(url, json={'query': query})
        response.raise_for_status()
    except Exception as e:
        print(f"Request failed: {e}")
        break  
    
    data = response.json()
    if 'errors' in data:
        print(f"GraphQL errors: {data['errors']}")
        break
    
    records = data.get('data', {}).get('pairDayDatas', [])
    if not records:
        print("No more records returned. Pagination complete.")
        break
    
    all_records.extend(records)
    
    last_date = records[-1]['date']
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump({"last_timestamp": last_date}, f)
    
    if len(records) < 1000:
        print("Fetched final batch of records.")
        break
    
    start_timestamp = last_date + 1

if os.path.exists(CHECKPOINT_FILE):
    os.remove(CHECKPOINT_FILE)

df = pd.DataFrame(all_records)
df.to_excel(OUTPUT_EXCEL, index=False)
print(f"Saved {len(all_records)} records to {OUTPUT_EXCEL}")
