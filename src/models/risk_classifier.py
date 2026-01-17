"""
AEWS - Risk Classification Model
--------------------------------
Predicts next-month Aadhaar service stress level
using historical ISI and activity signals.
"""

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report


class RiskClassifier:
    def __init__(
        self,
        low_threshold: float = 0.33,
        high_threshold: float = 0.66,
        random_state: int = 42
    ):
        self.low_threshold = low_threshold
        self.high_threshold = high_threshold

        self.model = RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            random_state=random_state,
            class_weight="balanced"
        )

    def create_risk_labels(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert ISI score into categorical risk labels
        """
        df = df.copy()

        def label_risk(isi):
            if isi <= self.low_threshold:
                return 0   # Low
            elif isi <= self.high_threshold:
                return 1   # Medium
            else:
                return 2   # High

        df["risk_label"] = df["isi_score"].apply(label_risk)
        return df

    def prepare_training_data(
        self,
        df: pd.DataFrame,
        feature_cols: list
    ):
        X = df[feature_cols]
        y = df["risk_label"]
        return X, y

    def train(
        self,
        X: pd.DataFrame,
        y: pd.Series
    ):
        self.model.fit(X, y)

    def evaluate(
        self,
        X_test: pd.DataFrame,
        y_test: pd.Series
    ):
        preds = self.model.predict(X_test)
        print(classification_report(y_test, preds))

    def predict(self, X: pd.DataFrame):
        return self.model.predict(X)
