# I used this script to obtain all liquidity variables between the start ad end block. In the end I started using liquidity.py since that script only obtains the liquidity variable for specific block numbers

import requests
import pandas as pd

API_KEY = "#INSERT API KEY"
SUBGRAPH_ID = "5zvR82QoaXYFyDEKLZ9t6v9adgnptxYpKpSbxtgVENFV"
POOL_ID = "0x4585fe77225b41b697c938b018e2ac67ac5a20c0".lower()  
START_BLOCK = 17816537 
END_BLOCK   = 18908832
BATCH_SIZE  = 100    

url = f"https://gateway.thegraph.com/api/{API_KEY}/subgraphs/id/{SUBGRAPH_ID}"

results = []  


current_block = START_BLOCK
while current_block <= END_BLOCK:
    batch_end = min(current_block + BATCH_SIZE - 1, END_BLOCK)
    block_range = range(current_block, batch_end + 1)
    query_parts = []
    for block_num in block_range:
        alias = f"b{block_num}"  
        query_parts.append(f'{alias}: pool(id: "{POOL_ID}", block: {{ number: {block_num} }}) {{ liquidity }}')
    query_string = "{\n" + "\n".join(query_parts) + "\n}"
    response = requests.post(url, json={'query': query_string})
    if response.status_code != 200 or 'errors' in response.json():
        print(f"Error querying blocks {current_block} to {batch_end}: {response.text}")
        break
    
    data = response.json().get('data', {})
    for block_num in block_range:
        alias = f"b{block_num}"
        pool_data = data.get(alias)
        if pool_data is None:
            continue
        liquidity = pool_data.get('liquidity')
        results.append((block_num, liquidity))
    print(f"Fetched blocks {current_block} to {batch_end}")
    current_block = batch_end + 1


df = pd.DataFrame(results, columns=['Block', 'Liquidity'])

output_file = "uniswap_v3_pool_liquidity.xlsx"
df.to_excel(output_file, index=False)
print(f"Results saved to {output_file}")
