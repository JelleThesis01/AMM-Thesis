#I use this script to obtain the positions of the LPs for v3.

import requests
import pandas as pd

API_KEY       = "#INSERT API KEY"
SUBGRAPH_ID   = "5zvR82QoaXYFyDEKLZ9t6v9adgnptxYpKpSbxtgVENFV"
POOL_ID       = "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640"
BLOCK_NUMBER  = 18172614

GRAPHQL_URL = f"https://gateway.thegraph.com/api/{API_KEY}/subgraphs/id/{SUBGRAPH_ID}"

pool_query = """
query getPool($id: ID!, $blockNum: Int!) {
  pool(id: $id, block: { number: $blockNum }) {
    liquidity
    totalValueLockedUSD
  }
}
"""

r = requests.post(GRAPHQL_URL, json={
    "query": pool_query,
    "variables": {"id": POOL_ID, "blockNum": BLOCK_NUMBER}
})
r.raise_for_status()
pool_data = r.json()["data"]["pool"]
global_liquidity   = float(pool_data["liquidity"])
global_tvl_usd     = float(pool_data["totalValueLockedUSD"])
position_query = """
query getPositions($lastID: ID!, $blockNum: Int!) {
  positions(
    first: 1000,
    where: { pool: "%s", id_gt: $lastID },
    block: { number: $blockNum }
  ) {
    id
    owner
    liquidity
  }
}
""" % POOL_ID

positions = []
last_id = ""
while True:
    resp = requests.post(GRAPHQL_URL, json={
        "query": position_query,
        "variables": {"lastID": last_id, "blockNum": BLOCK_NUMBER}
    })
    resp.raise_for_status()
    batch = resp.json()["data"]["positions"]
    if not batch:
        break
    positions.extend(batch)
    last_id = batch[-1]["id"]
    if len(batch) < 1000:
        break

df = pd.DataFrame(positions)
df["liquidity"] = df["liquidity"].astype(float)
df["usd_value"] = df["liquidity"] / global_liquidity * global_tvl_usd
df.rename(columns={
    "id": "Position ID",
    "owner": "Owner",
    "liquidity": "Liquidity"
}, inplace=True)


output_filename = "uniswap_v3_lp_usd_shares.xlsx"
df[["Position ID", "Owner", "Liquidity", "usd_value"]].to_excel(
    output_filename, index=False
)

print(f"Wrote {len(df)} positions to {output_filename}")
