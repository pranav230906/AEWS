"""
AEWS - Identity Stress Index (ISI)
---------------------------------
Computes a composite stress score that represents
identity volatility and operational pressure.
"""

import pandas as pd
from sklearn.preprocessing import MinMaxScaler


class IdentityStressIndex:
    def __init__(
        self,
        demo_weight: float = 0.4,
        bio_weight: float = 0.4,
        enrol_weight: float = 0.2
    ):
        """
        Weights must sum to 1.0
        """
        if round(demo_weight + bio_weight + enrol_weight, 2) != 1.0:
            raise ValueError("ISI weights must sum to 1.0")

        self.demo_weight = demo_weight
        self.bio_weight = bio_weight
        self.enrol_weight = enrol_weight

        self.scaler = MinMaxScaler()

    def _normalize(self, series: pd.Series) -> pd.Series:
        values = series.values.reshape(-1, 1)
        return pd.Series(
            self.scaler.fit_transform(values).flatten(),
            index=series.index
        )

    def compute(
        self,
        enrol_df: pd.DataFrame,
        demo_df: pd.DataFrame,
        bio_df: pd.DataFrame,
        group_cols: list = ["state", "district", "year_month"]
    ) -> pd.DataFrame:
        """
        Compute ISI at monthly level
        """

        # Select numeric activity columns
        enrol_col = enrol_df.select_dtypes(include="number").sum(axis=1)
        demo_col = demo_df.select_dtypes(include="number").sum(axis=1)
        bio_col = bio_df.select_dtypes(include="number").sum(axis=1)

        isi_df = enrol_df[group_cols].copy()

        isi_df["enrol_activity"] = enrol_col
        isi_df["demo_activity"] = demo_col
        isi_df["bio_activity"] = bio_col

        # Normalize
        isi_df["enrol_norm"] = self._normalize(isi_df["enrol_activity"])
        isi_df["demo_norm"] = self._normalize(isi_df["demo_activity"])
        isi_df["bio_norm"] = self._normalize(isi_df["bio_activity"])

        # ISI formula
        isi_df["isi_score"] = (
            self.demo_weight * isi_df["demo_norm"] +
            self.bio_weight * isi_df["bio_norm"] -
            self.enrol_weight * isi_df["enrol_norm"]
        )

        return isi_df
