#This is the most important script (toghether with the one for v3). I used this to obtain all swaps from the Uniswap v2 pools. This script to obtains all the variables between certain timestamps.

import requests
import pandas as pd
import os

API_KEY = "#INSERT API KEY"  
SUBGRAPH_ID = "EYCKATKGBKLWvSfwvBjzfCBmGwYNdVkduYXVivCsLRFu"  
GRAPH_ENDPOINT = f"https://gateway.thegraph.com/api/{API_KEY}/subgraphs/id/{SUBGRAPH_ID}"

PAIR_ID = "0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc".lower()  
START_TIMESTAMP = 1627776000                        
END_TIMESTAMP = 1635724800                              

OUTPUT_FILE = "MONTH_v2_USCC_eth_swaps.xlsx"

last_timestamp = START_TIMESTAMP
all_swaps_df = pd.DataFrame()  

if os.path.exists(OUTPUT_FILE):
    try:
        existing_df = pd.read_excel(OUTPUT_FILE)
        if not existing_df.empty:
            all_swaps_df = existing_df
            max_ts = existing_df["timestamp"].max()
            if pd.notna(max_ts):
                last_timestamp = int(max_ts)
                print(f"Resuming from last timestamp {last_timestamp}...")
    except Exception as e:
        print(f"Warning: Could not read existing output file. Starting from beginning. ({e})")

graphql_query = """
query($pair: ID!, $lastTs: BigInt!, $endTs: BigInt!) {
  swaps(
    first: 1000, 
    orderBy: timestamp, 
    orderDirection: asc, 
    where: {
      pair: $pair, 
      timestamp_gt: $lastTs, 
      timestamp_lte: $endTs
    }
  ) {
    id
    timestamp
    sender
    to
    amount0In
    amount1In
    amount0Out
    amount1Out
    amountUSD
    logIndex
    transaction {
      id
      blockNumber
    }
    pair {
      id
    }
  }
}
"""

print("Starting data fetch from The Graph...")
has_more = True
batch_count = 0
new_records = 0

while has_more:
    variables = {
        "pair": PAIR_ID,
        "lastTs": last_timestamp if batch_count > 0 else START_TIMESTAMP,  
        "endTs": END_TIMESTAMP
    }
    if batch_count == 0:
        variables["lastTs"] = START_TIMESTAMP - 1
    
    try:
        response = requests.post(GRAPH_ENDPOINT, json={"query": graphql_query, "variables": variables})
    except Exception as e:
        print(f"Request failed: {e}")
        break
    if response.status_code != 200 or "errors" in response.text:
        print(f"GraphQL query error (status {response.status_code}): {response.text}")
        break
    
    data = response.json().get("data", {})
    swaps = data.get("swaps", [])
    if not swaps:
        has_more = False
        print("No more swaps found, reached end of data range.")
        break
    
    batch_df = pd.DataFrame(swaps)
    batch_df["timestamp"] = pd.to_numeric(batch_df["timestamp"])
    batch_df["logIndex"] = pd.to_numeric(batch_df["logIndex"])
    if all_swaps_df.empty:
        all_swaps_df = batch_df
    else:
        all_swaps_df = pd.concat([all_swaps_df, batch_df], ignore_index=True)
    
    batch_count += 1
    new_records += len(batch_df)
    last_timestamp = int(batch_df["timestamp"].iloc[-1])  
    total_fetched = len(all_swaps_df)
    print(f"Batch {batch_count}: fetched {len(batch_df)} swaps (total collected so far: {total_fetched})")
    if last_timestamp >= END_TIMESTAMP:
        print("Reached the end timestamp limit.")
        has_more = False
        break


if not all_swaps_df.empty:
    try:
        all_swaps_df.drop_duplicates(subset="id", inplace=True)
        all_swaps_df.sort_values("timestamp", inplace=True)
        all_swaps_df.reset_index(drop=True, inplace=True)
        all_swaps_df.to_excel(OUTPUT_FILE, index=False)
        print(f"\nData collection complete. Total swaps fetched: {len(all_swaps_df)}")
        print(f"Saved results to {OUTPUT_FILE}")
    except Exception as e:
        print(f"Failed to write to Excel: {e}")
else:
    print("No swap data collected (no output file created).")
