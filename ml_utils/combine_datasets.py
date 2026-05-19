import argparse
import pandas as pd
from pathlib import Path
 
 
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-inputs', nargs='+', required=True, help='CSV files to combine')
    parser.add_argument('-output', required=True, help='Output filename')
    args = parser.parse_args()
 
    df_list = []
    for path in args.inputs:
        p = Path(path)
        if not p.exists():
            print(f'Warning: {p} not found, skipping.')
            continue
        df_list.append(pd.read_csv(p))
        print(f'Loaded {p} ({len(df_list[-1]):,} rows)')
 
    if not df_list:
        print('No input files loaded. Exiting.')
        raise SystemExit(1)
 
    combined = pd.concat(df_list, ignore_index=True)
    combined.to_csv(args.output, index=False)
    print(f'Saved {args.output} ({len(combined):,} rows total)')
 