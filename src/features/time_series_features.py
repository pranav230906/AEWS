"""
AEWS - Time Series Feature Engineering
-------------------------------------
Creates lag, rolling, and growth-based features
from monthly Aadhaar datasets.
"""

import pandas as pd


class TimeSeriesFeatureEngineer:
    def __init__(self, time_col: str = "year_month"):
        self.time_col = time_col

    @staticmethod
    def _ensure_datetime(df: pd.DataFrame, time_col: str) -> pd.DataFrame:
        df = df.copy()
        df[time_col] = pd.to_datetime(df[time_col])
        return df

    def add_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Adds month number for seasonality
        """
        df = df.copy()
        df[self.time_col] = pd.to_datetime(df[self.time_col])
        df["month"] = df[self.time_col].dt.month
        return df

    def add_lag_features(
        self,
        df: pd.DataFrame,
        group_cols: list,
        target_cols: list,
        lags: list = [1, 2, 12]
    ) -> pd.DataFrame:
        """
        Create lag features (t-1, t-2, t-12)
        """
        df = df.copy()
        df = self._ensure_datetime(df, self.time_col)

        df = df.sort_values(group_cols + [self.time_col])

        for col in target_cols:
            for lag in lags:
                df[f"{col}_lag_{lag}"] = (
                    df.groupby(group_cols)[col]
                    .shift(lag)
                )

        return df

    def add_rolling_features(
        self,
        df: pd.DataFrame,
        group_cols: list,
        target_cols: list,
        windows: list = [3, 6]
    ) -> pd.DataFrame:
        """
        Create rolling mean features
        """
        df = df.copy()
        df = self._ensure_datetime(df, self.time_col)

        for col in target_cols:
            for window in windows:
                df[f"{col}_roll_{window}"] = (
                    df
                    .groupby(group_cols)[col]
                    .rolling(window)
                    .mean()
                    .reset_index(level=group_cols, drop=True)
                )

        return df

    def add_growth_rate(
        self,
        df: pd.DataFrame,
        group_cols: list,
        target_cols: list
    ) -> pd.DataFrame:
        """
        Month-over-month growth rate
        """
        df = df.copy()
        df = self._ensure_datetime(df, self.time_col)

        for col in target_cols:
            df[f"{col}_growth"] = (
                df
                .groupby(group_cols)[col]
                .pct_change()
            )

        return df
