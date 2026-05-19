import argparse
import pandas as pd
from pathlib import Path

def flatten_csv_logs(output_name: str = 'move_data.csv'):
    log_dir = Path.cwd() / 'logs'
    csv_files = list(log_dir.glob('*.csv'))
 
    if not csv_files:
        print('No CSV files found in logs/. Skipping merge.')
        return
 
    df_list = []
    for file in csv_files:
        df = pd.read_csv(file)
        df['Game Result'] = df['Game Status'].iloc[-1]
        df['Total Turns'] = len(df)
        df_list.append(df)
 
    combined_df = pd.concat(df_list, ignore_index=True)
    combined_df.to_csv(output_name, index=False)
    print(f'Combined {len(csv_files)} CSV files into {output_name}. Total rows: {len(combined_df)}.')
 
 
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-name', default='move_data.csv')
    args = parser.parse_args()
    flatten_csv_logs(args.name)