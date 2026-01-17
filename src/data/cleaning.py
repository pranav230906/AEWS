"""
AEWS - Data Cleaning & Aggregation
---------------------------------
Cleans raw Aadhaar datasets and aggregates them to monthly granularity.
"""

import pandas as pd
from pathlib import Path


class DataCleaner:
    def __init__(self, output_dir: str = "data/processed"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # ---------- Helpers ----------

    @staticmethod
    def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df.columns = (
            df.columns
            .str.strip()
            .str.lower()
            .str.replace(" ", "_")
        )
        return df

    @staticmethod
    def normalize_text(series: pd.Series) -> pd.Series:
        return (
            series.astype(str)
            .str.strip()
            .str.title()
        )

    @staticmethod
    def parse_date_column(df: pd.DataFrame) -> pd.DataFrame:
        date_candidates = [
            "date", "created_date", "created_at",
            "enrolment_date", "update_date"
        ]

        for col in date_candidates:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")
                df["year_month"] = df[col].dt.to_period("M").astype(str)
                return df

        raise ValueError("❌ No recognizable date column found")

    # ---------- Main Cleaning ----------

    def clean_common(self, df: pd.DataFrame) -> pd.DataFrame:
        df = self.standardize_columns(df)

        if "state" in df.columns:
            df["state"] = self.normalize_text(df["state"])

        if "district" in df.columns:
            df["district"] = self.normalize_text(df["district"])

        df = self.parse_date_column(df)

        return df

    def aggregate_monthly(self, df: pd.DataFrame) -> pd.DataFrame:
        group_cols = ["state", "district", "year_month"]
        group_cols = [c for c in group_cols if c in df.columns]

        numeric_cols = df.select_dtypes(include="number").columns

        monthly_df = (
            df
            .groupby(group_cols)[numeric_cols]
            .sum()
            .reset_index()
        )

        return monthly_df

    # ---------- Public API ----------

    def clean_and_save(self, df: pd.DataFrame, output_name: str) -> pd.DataFrame:
        df = self.clean_common(df)
        df = self.aggregate_monthly(df)

        output_path = self.output_dir / output_name
        df.to_csv(output_path, index=False)

        print(f"✔ Saved → {output_path}")
        return df
