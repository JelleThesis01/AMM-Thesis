#I use this script to obtain the liquidity variable for certain block numbers, You need the excel file Blocknumbers.xlsx as well

import os
import argparse
import requests
import pandas as pd

API_KEY = os.getenv('API_KEY', '#INSERT API KEY')
SUBGRAPH_ID = os.getenv('SUBGRAPH_ID', '5zvR82QoaXYFyDEKLZ9t6v9adgnptxYpKpSbxtgVENFV')
POOL_ID = os.getenv('POOL_ID', '0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640').lower()


def load_blocks(blocks_path):
    """
    Load block numbers from a CSV, Excel, or TXT file.
    Expects either a column named 'Block' (case-insensitive) in tabular formats,
    or one block number per line in a TXT file.
    """
    ext = os.path.splitext(blocks_path)[1].lower()
    if ext in ['.xlsx', '.xls']:
        df = pd.read_excel(blocks_path)
        cols_lower = [str(c).lower() for c in df.columns]
        if 'block' in cols_lower:
            col = df.columns[cols_lower.index('block')]
            block_list = df[col].dropna().astype(int).tolist()
        else:
            block_list = pd.to_numeric(df.iloc[:, 0], errors='coerce').dropna().astype(int).tolist()
    elif ext == '.csv':
        df = pd.read_csv(blocks_path)
        cols_lower = [str(c).lower() for c in df.columns]
        if 'block' in cols_lower:
            col = df.columns[cols_lower.index('block')]
            block_list = df[col].dropna().astype(int).tolist()
        else:
            block_list = pd.to_numeric(df.iloc[:, 0], errors='coerce').dropna().astype(int).tolist()
    elif ext == '.txt':
        with open(blocks_path, 'r') as f:
            block_list = [int(line.strip()) for line in f if line.strip()]
    else:
        raise ValueError(f"Unsupported file extension: {ext}")
    return sorted(set(block_list))


def fetch_liquidity(blocks, api_key, subgraph_id, pool_id, batch_size):
    """
    Fetch liquidity for a given pool at specific blocks in batches.
    """
    url = f"https://gateway.thegraph.com/api/{api_key}/subgraphs/id/{subgraph_id}"
    results = []
    for i in range(0, len(blocks), batch_size):
        batch = blocks[i:i + batch_size]
        query_parts = []
        for bn in batch:
            alias = f"b{bn}"
            query_parts.append(
                f"{alias}: pool(id: \"{pool_id}\", block: {{ number: {bn} }}) {{ liquidity }}"
            )
        query_string = "{\n" + "\n".join(query_parts) + "\n}"
        response = requests.post(url, json={'query': query_string})
        if response.status_code != 200 or 'errors' in response.json():
            print(f"Error querying blocks {batch[0]} to {batch[-1]}: {response.text}")
            break
        data = response.json().get('data', {})
        for bn in batch:
            alias = f"b{bn}"
            pool_data = data.get(alias)
            if pool_data and 'liquidity' in pool_data:
                results.append((bn, pool_data['liquidity']))

        print(f"Fetched blocks {batch[0]} to {batch[-1]}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Fetch Uniswap V3 pool liquidity at specific blocks"
    )
    parser.add_argument(
        '--blocks-file', '-b', default=os.path.expanduser('~/Desktop/blocknumbers.xlsx'),
        help="Path to CSV, Excel (.xlsx/.xls), or .txt file listing block numbers (default: ~/Desktop/blocknumbers.xlsx)"
    )
    parser.add_argument(
        '--output', '-o', default="uniswap_v3_pool_liquidity.xlsx",
        help="Output Excel filename"
    )
    parser.add_argument(
        '--batch-size', '-n', type=int, default=100,
        help="Number of blocks per GraphQL batch"
    )
    args = parser.parse_args()

    blocks = load_blocks(args.blocks_file)
    print(f"Loaded {len(blocks)} unique blocks from {args.blocks_file}")

    results = fetch_liquidity(
        blocks, API_KEY, SUBGRAPH_ID, POOL_ID, args.batch_size
    )

    df = pd.DataFrame(results, columns=['Block', 'Liquidity'])
    df.to_excel(args.output, index=False)
    print(f"Results saved to {args.output}")


if __name__ == "__main__":
    main()
