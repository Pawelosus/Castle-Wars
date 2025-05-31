import torch
from torch.utils.data import Dataset
import pandas as pd
from ast import literal_eval
from ml_utils.feature_processing import build_feature_tensor

class MoveDataset(Dataset):
    def __init__(self, csv_file):
        self.data = pd.read_csv(csv_file)
        self._preprocess_data()

    def _preprocess_data(self):
        """Convert and normalize all data upfront."""
        # Resources: String -> List[int]
        self.data['Player Resources'] = self.data['Player Resources'].apply(literal_eval)
        self.data['Opponent Resources'] = self.data['Opponent Resources'].apply(literal_eval)
        self.data['Player Hand'] = self.data['Player Hand'].apply(literal_eval)

        # Precompute labels
        self.data['Label'] = self.data.apply(
            lambda row: 1.0 if row['Current Player'] == row['Game Result'] else -1.0,
            axis=1
        )


    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        row = self.data.iloc[idx]

        return (
            build_feature_tensor(features=row),
            torch.tensor(row['Label'], dtype=torch.float32)
        )
