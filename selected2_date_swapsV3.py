#This is the most important script (toghether with the one for v2). I used this to obtain all swaps from the Uniswap v3 pools. This script to obtains all the variables between certain timestamps.

import requests
import pandas as pd
import os

GRAPHQL_URL = "https://gateway.thegraph.com/api/#INSERT API KEY/subgraphs/id/5zvR82QoaXYFyDEKLZ9t6v9adgnptxYpKpSbxtgVENFV"
POOL_ID = "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640"  
START_TIMESTAMP = 1633046400                                                        
END_TIMESTAMP   = 1635724800                                                        
PROGRESS_FILE = "progress.txt"
OUTPUT_FILE = "month_ETH_swapdata_v3.xlsx"

try:
    query_pool = f"""
    {{
      pool(id: "{POOL_ID}") {{
        token0 {{ id symbol name decimals }}
        token1 {{ id symbol name decimals }}
        feeTier
      }}
    }}
    """
    resp = requests.post(GRAPHQL_URL, json={'query': query_pool})
    data = resp.json()
    if 'errors' in data:
        raise Exception(f"GraphQL error: {data['errors']}")
    pool_info = data.get('data', {}).get('pool')
    if pool_info:
        print("Pool info fetched successfully:")
        print(f"  Token0: {pool_info['token0']}")
        print(f"  Token1: {pool_info['token1']}")
        print(f"  Fee Tier: {pool_info['feeTier']}")
    else:
        print("Warning: Could not fetch pool info.")
except Exception as e:
    print(f"Error fetching pool info: {e}")

current_start = START_TIMESTAMP
if os.path.exists(PROGRESS_FILE):
    try:
        with open(PROGRESS_FILE, "r") as pf:
            line = pf.readline().strip()
            if line:
                last_ts = int(line)
                if last_ts >= START_TIMESTAMP and last_ts < END_TIMESTAMP:
                    current_start = last_ts + 1
                    print(f"Resuming from timestamp {current_start} (after {last_ts}) based on progress file.")
                else:
                    print("Progress file timestamp is outside the specified range; starting from beginning.")
            else:
                print("Progress file is empty; starting from beginning.")
    except Exception as e:
        print(f"Could not read progress file, starting from {START_TIMESTAMP}. Error: {e}")

all_swaps = []
total_count = 0


try:
    while current_start <= END_TIMESTAMP:
        query = f"""
        {{
          swaps(first: 1000, orderBy: timestamp, orderDirection: asc, 
                where: {{ pool: "{POOL_ID}", timestamp_gte: {current_start}, timestamp_lte: {END_TIMESTAMP} }}) 
          {{
            id
            timestamp
            sender
            recipient
            origin
            amount0
            amount1
            amountUSD
            sqrtPriceX96
            tick
            logIndex
            token0 {{ id symbol name decimals }}
            token1 {{ id symbol name decimals }}
            pool {{ id feeTier token0 {{ id symbol }} token1 {{ id symbol }} }}
            transaction {{ id blockNumber gasUsed gasPrice }}
          }}
        }}
        """
        response = requests.post(GRAPHQL_URL, json={'query': query})
        result = response.json()
        if 'errors' in result:
            raise Exception(f"GraphQL query error: {result['errors']}")
        swaps_batch = result.get('data', {}).get('swaps', [])
        if not swaps_batch:
            break

        for swap in swaps_batch:
            swap_record = {
                "id": swap.get("id"),
                "timestamp": int(swap.get("timestamp")),
                "sender": swap.get("sender"),
                "recipient": swap.get("recipient"),
                "origin": swap.get("origin"),
                "amount0": float(swap["amount0"]) if swap.get("amount0") else None,
                "amount1": float(swap["amount1"]) if swap.get("amount1") else None,
                "amountUSD": float(swap["amountUSD"]) if swap.get("amountUSD") else None,
                "sqrtPriceX96": swap.get("sqrtPriceX96"),
                "tick": swap.get("tick"),
                "logIndex": swap.get("logIndex"),
                "token0_id": swap.get("token0", {}).get("id"),
                "token0_symbol": swap.get("token0", {}).get("symbol"),
                "token0_name": swap.get("token0", {}).get("name"),
                "token0_decimals": swap.get("token0", {}).get("decimals"),
                "token1_id": swap.get("token1", {}).get("id"),
                "token1_symbol": swap.get("token1", {}).get("symbol"),
                "token1_name": swap.get("token1", {}).get("name"),
                "token1_decimals": swap.get("token1", {}).get("decimals"),
                "pool_id": swap.get("pool", {}).get("id"),
                "pool_feeTier": swap.get("pool", {}).get("feeTier"),
                "pool_token0_id": swap.get("pool", {}).get("token0", {}).get("id"),
                "pool_token0_symbol": swap.get("pool", {}).get("token0", {}).get("symbol"),
                "pool_token1_id": swap.get("pool", {}).get("token1", {}).get("id"),
                "pool_token1_symbol": swap.get("pool", {}).get("token1", {}).get("symbol"),
                "transaction_id": swap.get("transaction", {}).get("id"),
                "transaction_blockNumber": swap.get("transaction", {}).get("blockNumber"),
                "transaction_gasUsed": swap.get("transaction", {}).get("gasUsed"),
                "transaction_gasPrice": swap.get("transaction", {}).get("gasPrice")
            }
            all_swaps.append(swap_record)
        total_count += len(swaps_batch)
        last_fetched_ts = int(swaps_batch[-1]['timestamp'])
        last_fetched_id = swaps_batch[-1]['id']

        print(f"Fetched {len(swaps_batch)} swaps (total so far: {total_count}) up to timestamp {last_fetched_ts}")

    
        with open(PROGRESS_FILE, "w") as pf:
            pf.write(str(last_fetched_ts))
        if len(swaps_batch) < 1000:
            break
        last_ts = last_fetched_ts
        while True:
            query_same_ts = f"""
            {{
              swaps(first: 1000, orderBy: id, orderDirection: asc,
                    where: {{ pool: "{POOL_ID}", timestamp: {last_ts}, id_gt: "{last_fetched_id}" }})
              {{
                id
                timestamp
                sender
                recipient
                origin
                amount0
                amount1
                amountUSD
                sqrtPriceX96
                tick
                logIndex
                token0 {{ id symbol name decimals }}
                token1 {{ id symbol name decimals }}
                pool {{ id feeTier token0 {{ id symbol }} token1 {{ id symbol }} }}
                transaction {{ id blockNumber gasUsed gasPrice }}
              }}
            }}
            """
            resp2 = requests.post(GRAPHQL_URL, json={'query': query_same_ts})
            res2 = resp2.json()
            if 'errors' in res2:
                raise Exception(f"GraphQL query error (same timestamp): {res2['errors']}")
            swaps_same_ts = res2.get('data', {}).get('swaps', [])
            if not swaps_same_ts:
                break
            for swap in swaps_same_ts:
                swap_record = {
                    "id": swap.get("id"),
                    "timestamp": int(swap.get("timestamp")),
                    "sender": swap.get("sender"),
                    "recipient": swap.get("recipient"),
                    "origin": swap.get("origin"),
                    "amount0": float(swap["amount0"]) if swap.get("amount0") else None,
                    "amount1": float(swap["amount1"]) if swap.get("amount1") else None,
                    "amountUSD": float(swap["amountUSD"]) if swap.get("amountUSD") else None,
                    "sqrtPriceX96": swap.get("sqrtPriceX96"),
                    "tick": swap.get("tick"),
                    "logIndex": swap.get("logIndex"),
                    "token0_id": swap.get("token0", {}).get("id"),
                    "token0_symbol": swap.get("token0", {}).get("symbol"),
                    "token0_name": swap.get("token0", {}).get("name"),
                    "token0_decimals": swap.get("token0", {}).get("decimals"),
                    "token1_id": swap.get("token1", {}).get("id"),
                    "token1_symbol": swap.get("token1", {}).get("symbol"),
                    "token1_name": swap.get("token1", {}).get("name"),
                    "token1_decimals": swap.get("token1", {}).get("decimals"),
                    "pool_id": swap.get("pool", {}).get("id"),
                    "pool_feeTier": swap.get("pool", {}).get("feeTier"),
                    "pool_token0_id": swap.get("pool", {}).get("token0", {}).get("id"),
                    "pool_token0_symbol": swap.get("pool", {}).get("token0", {}).get("symbol"),
                    "pool_token1_id": swap.get("pool", {}).get("token1", {}).get("id"),
                    "pool_token1_symbol": swap.get("pool", {}).get("token1", {}).get("symbol"),
                    "transaction_id": swap.get("transaction", {}).get("id"),
                    "transaction_blockNumber": swap.get("transaction", {}).get("blockNumber"),
                    "transaction_gasUsed": swap.get("transaction", {}).get("gasUsed"),
                    "transaction_gasPrice": swap.get("transaction", {}).get("gasPrice")
                }
                all_swaps.append(swap_record)
            total_count += len(swaps_same_ts)
            last_fetched_id = swaps_same_ts[-1]['id']
            print(f"  Fetched {len(swaps_same_ts)} additional swaps at timestamp {last_ts} (total so far: {total_count})")
            with open(PROGRESS_FILE, "w") as pf:
                pf.write(str(last_ts))
            if len(swaps_same_ts) < 1000:
                break

        
        current_start = last_ts + 1
        if current_start > END_TIMESTAMP:
            break
except Exception as e:
    print(f"Error during fetching swaps: {e}")


if all_swaps:
    df = pd.DataFrame(all_swaps)
    df.sort_values("timestamp", inplace=True)
    df.to_excel(OUTPUT_FILE, index=False)
    print(f"\nDone! Total swaps fetched: {len(df)}. Data saved to {OUTPUT_FILE}")
else:
    print("No swap data found for the specified pool and time range.")
