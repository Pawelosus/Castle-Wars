import argparse
import shutil
from pathlib import Path
 
 
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-source', required=True, help='File to archive (e.g. move_data.csv)')
    parser.add_argument('-generation', type=int, required=True)
    args = parser.parse_args()
 
    src = Path(args.source)
    dest_dir = Path('archives') / f'gen_{args.generation}'
    dest_dir.mkdir(parents=True, exist_ok=True)
 
    dest = dest_dir / src.name
    shutil.copy(src, dest)
    print(f'Archived {src} -> {dest}')
 