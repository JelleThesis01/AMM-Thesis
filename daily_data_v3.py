# I used this script to obtain daily data from a Uniswap v3 pool. Daily data can be anything specified under query. To use this script you would need to insert your own API key and specify the timestamp.

import requests
import pandas as pd

API_KEY = "#INSERT API KEY"  
SUBGRAPH_ID = "5zvR82QoaXYFyDEKLZ9t6v9adgnptxYpKpSbxtgVENFV"  
url = f"https://gateway.thegraph.com/api/{API_KEY}/subgraphs/id/{SUBGRAPH_ID}"

query = """
query($poolId: ID!, $lastTimestamp: Int!) {
  poolDayDatas(
    first: 1000,
    orderBy: date,
    orderDirection: asc,
    where: { pool: $poolId, date_gt: $lastTimestamp }
  ) {
    date
    liquidity
    sqrtPrice
    token0Price
    token1Price
    volumeToken0
    volumeToken1
    tvlUSD
    tick
  }
}
"""

variables = {
    "poolId": "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640",  
    "lastTimestamp": #Timestamp   
}

all_data = []

while True:
    response = requests.post(url, json={"query": query, "variables": variables})
    if response.status_code != 200:
        print(f"Request failed with status {response.status_code}: {response.text}")
        break  
    
    result = response.json()
    if "errors" in result:
        print(f"GraphQL errors encountered: {result['errors']}")
        break  
    
    day_data = result.get("data", {}).get("poolDayDatas", [])
    if not day_data:
        break
    
    all_data.extend(day_data)
    
    last_date = day_data[-1]["date"]
    variables["lastTimestamp"] = int(last_date)  
    
    if len(day_data) < 1000:
        break

df = pd.DataFrame(all_data)

output_filename = "uniswap_v3_usdc_weth_pool_day_data.xlsx"
df.to_excel(output_filename, index=False)
print(f"Data successfully written to {output_filename}")
