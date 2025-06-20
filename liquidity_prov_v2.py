#I use this script to obtain the positions of the LPs for v2.

import sys
import requests
import pandas as pd
from decimal import Decimal


POOL_ID      = "0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc"
BLOCK_NUMBER = 18172614
API_KEY      = "#INSERT API KEY"

if len(sys.argv) == 4:
    POOL_ID      = sys.argv[1]
    BLOCK_NUMBER = int(sys.argv[2])
    API_KEY      = sys.argv[3]
elif len(sys.argv) not in (1, 4):
    print("Usage: python3 liquidity_prov_V2.py [POOL_ID BLOCK API_KEY]")
    sys.exit(1)


pool_id = POOL_ID.lower()

print(f"\n▶ Querying pool {pool_id} at block {BLOCK_NUMBER}")


GRAPH_URL = (
    f"https://gateway.thegraph.com/api/{API_KEY}"
    "/subgraphs/id/A3Np3RQbaBA6oKJgiwDJeo5T3zrYfGHPWFYayMwtNDum"
)

query_pool = {
    "query": """
      query($id: ID!, $block: Int!) {
        pair(id: $id, block: {number: $block}) {
          totalSupply
          reserveUSD
        }
      }
    """,
    "variables": {"id": pool_id, "block": BLOCK_NUMBER},
}
resp = requests.post(GRAPH_URL, json=query_pool)
resp.raise_for_status()
payload = resp.json()
if "errors" in payload:
    print("GraphQL error while fetching pool data:", payload["errors"])
    sys.exit(1)
pair = payload["data"]["pair"]
if pair is None:
    print("No pool data returned – check pool ID and block height.")
    sys.exit(1)
total_supply = Decimal(pair["totalSupply"])
reserve_usd  = Decimal(pair["reserveUSD"])
print(f"  • totalSupply : {total_supply}")
print(f"  • reserveUSD  : {reserve_usd}\n")


positions, page, BATCH = [], 0, 1000
print("▶ Fetching liquidity positions ...")
while True:
    query_pos = {
        "query": """
          query($id: ID!, $block: Int!, $first: Int!, $skip: Int!) {
            liquidityPositions(
              first:  $first,
              skip:   $skip,
              block:  {number: $block},
              where:  {pair: $id}
            ) {
              id                   # e.g. "0xabc…-0xb4e16…"
              liquidityTokenBalance
            }
          }
        """,
        "variables": {
            "id":    pool_id,
            "block": BLOCK_NUMBER,
            "first": BATCH,
            "skip":  page * BATCH,
        },
    }
    resp = requests.post(GRAPH_URL, json=query_pos)
    resp.raise_for_status()
    payload = resp.json()
    if "errors" in payload:
        print("GraphQL error on page", page, ":", payload["errors"])
        sys.exit(1)
    page_data = payload["data"]["liquidityPositions"]
    if not page_data:
        break
    positions.extend(page_data)
    print(f"  • page {page}  →  {len(page_data)} records")
    if len(page_data) < BATCH:
        break
    page += 1
print(f"✔ Total positions fetched: {len(positions)}\n")


records = []
for lp in positions:
    wallet   = lp["id"].split("-")[0]                
    balance  = Decimal(lp["liquidityTokenBalance"])
    share    = balance / total_supply if total_supply else Decimal(0)
    usd_val  = share * reserve_usd
    records.append(
        {
            "Wallet Address":   wallet,
            "LP Token Balance": float(balance),
            "USD Value":        float(usd_val),
        }
    )

df = pd.DataFrame(records)
outfile = f"uniswap_v2_lp_{pool_id[:6]}_{BLOCK_NUMBER}.xlsx"
df.to_excel(outfile, index=False)
print(f"✅  Results saved to {outfile}\n")

