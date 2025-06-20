# I used this script to obtain the amount of liquidity posted at every tick. To create the liquidity distribution graph. he eventual graph is created in Excel.

import requests
import pandas as pd

API_KEY      = "#INSERT API KEY"
SUBGRAPH_ID  = "5zvR82QoaXYFyDEKLZ9t6v9adgnptxYpKpSbxtgVENFV"
POOL_ADDRESS = "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640".lower()
BLOCK_NUMBER = 18172614 
OUTFILE      = "ticks_data.xlsx"


URL = f"https://gateway.thegraph.com/api/{API_KEY}/subgraphs/id/{SUBGRAPH_ID}"

QUERY = """
query($blockNumber: Int!, $poolAddress: String!, $skip: Int!) {
  ticks(
    block: { number: $blockNumber }
    where: { pool: $poolAddress }
    first: 1000
    skip: $skip
  ) {
    tickIdx
    liquidityNet
  }
}
"""

ticks, skip, errored = [], 0, False

while True:
    variables = {"blockNumber": BLOCK_NUMBER,
                 "poolAddress": POOL_ADDRESS,
                 "skip": skip}
    try:
        resp = requests.post(URL, json={"query": QUERY, "variables": variables})
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Network / HTTP error: {e}")
        errored = True
        break

    result = resp.json()
    if "errors" in result:
        print(f"GraphQL error: {result['errors']}")
        errored = True
        break

    batch = result.get("data", {}).get("ticks", [])
    if not batch:
        break                  
    ticks.extend(batch)
    skip += 1000              

if errored:
    print("Aborted – nothing exported.")
    exit()

ticks.sort(key=lambda t: int(t["tickIdx"]))

rows, cum_liq = [], 0
for t in ticks:
    tick_idx = int(t["tickIdx"])
    liq_net   = int(t["liquidityNet"])
    cum_liq  += liq_net
    rows.append({
        "tickIdx": tick_idx,
        "liquidityNet": liq_net,
        "cumulativeLiquidity": cum_liq
    })

df = pd.DataFrame(
    rows,
    columns=["tickIdx", "liquidityNet", "cumulativeLiquidity"]
)
df.to_excel(OUTFILE, index=False)
print(f"Success – {len(rows)} ticks written to {OUTFILE}")
