import pandas as pd
from pathlib import Path

# Set path to game log directory
log_dir = Path.cwd().parent / 'logs'

# Get all CSV files from the directory
csv_files = list(log_dir.glob('*.csv'))

# Read and concatenate all CSVs
df_list = []
for file in csv_files:
    df = pd.read_csv(file)

    # Add 'Game Result' column to each row
    game_result = df['Game Status'].iloc[-1]
    df['Game Result'] = game_result

    df_list.append(df)

combined_df = pd.concat(df_list, ignore_index=True)

# Output df as a file
output_file = Path('move_data.csv')
combined_df.to_csv(output_file, index=False)

print(f'Combined {len(csv_files)} CSV files into {output_file.name}. Total rows: {len(combined_df)}.')

