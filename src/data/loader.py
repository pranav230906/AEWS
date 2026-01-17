"""
AEWS - Data Loader
-----------------
Responsible ONLY for:
- Discovering chunked CSV files
- Loading them into pandas DataFrames
- Concatenating chunks safely

No cleaning or transformations happen here.
"""

import pandas as pd
from pathlib import Path
from typing import List


class DataLoader:
    def __init__(self, raw_data_dir: str):
        """
        Parameters
        ----------
        raw_data_dir : str
            Path to data/raw directory
        """
        self.raw_data_dir = Path(raw_data_dir)

    # ---------- Internal Helpers ----------

    def _get_csv_files(self, subfolder: str) -> List[Path]:
        """
        Get all CSV files inside a subfolder
        """
        folder_path = self.raw_data_dir / subfolder

        if not folder_path.exists():
            raise FileNotFoundError(f"Folder not found: {folder_path}")

        files = sorted(folder_path.glob("*.csv"))

        if not files:
            raise FileNotFoundError(f"No CSV files found in {folder_path}")

        return files

    def _load_and_concat(self, files: List[Path]) -> pd.DataFrame:
        """
        Load multiple CSV files and concatenate them
        """
        df_list = []

        print(f"Loading {len(files)} files...")
        for file in files:
            print(f"  → {file.name}")
            df = pd.read_csv(file)
            df_list.append(df)

        merged_df = pd.concat(df_list, ignore_index=True)
        return merged_df

    # ---------- Public Dataset Loaders ----------

    def load_enrolment_data(self) -> pd.DataFrame:
        """
        Load enrolment dataset (chunked)
        """
        files = self._get_csv_files("enrolment")
        return self._load_and_concat(files)

    def load_demographic_updates(self) -> pd.DataFrame:
        """
        Load demographic update dataset (chunked)
        """
        files = self._get_csv_files("demographic")
        return self._load_and_concat(files)

    def load_biometric_updates(self) -> pd.DataFrame:
        """
        Load biometric update dataset (chunked)
        """
        files = self._get_csv_files("biometric")
        return self._load_and_concat(files)

    def load_all(self):
        """
        Load all datasets together
        """
        return {
            "enrolment": self.load_enrolment_data(),
            "demographic": self.load_demographic_updates(),
            "biometric": self.load_biometric_updates(),
        }
