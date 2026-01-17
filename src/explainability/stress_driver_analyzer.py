"""
AEWS - Stress Driver Analyzer
-----------------------------
Explains WHY a district/state was flagged as high risk
using SHAP feature attribution.
"""

import shap
import pandas as pd
import numpy as np


class StressDriverAnalyzer:
    def __init__(self, model, feature_names: list):
        self.model = model
        self.feature_names = feature_names
        self.explainer = shap.TreeExplainer(model)

    def compute_shap_values(self, X: pd.DataFrame):
        return self.explainer.shap_values(X)

    def explain_instance(
        self,
        X: pd.DataFrame,
        index: int,
        class_id: int = 2
    ) -> pd.DataFrame:
        """
        Robust SHAP explanation for multiclass tree models
        (works across SHAP versions)
        """

        shap_values = self.compute_shap_values(X)

        # ---- HANDLE ALL SHAP OUTPUT FORMATS ----
        if isinstance(shap_values, list):
            # Case 1: List of arrays [n_classes][n_samples][n_features]
            values = shap_values[class_id][index]

        elif isinstance(shap_values, np.ndarray):
            # Case 2: Single array [n_samples][n_features][n_classes]
            if shap_values.ndim == 3:
                values = shap_values[index, :, class_id]
            else:
                raise ValueError(f"Unexpected SHAP array shape: {shap_values.shape}")

        else:
            raise TypeError("Unknown SHAP output type")

        # ---- SAFETY CHECK ----
        if len(values) != len(self.feature_names):
            raise ValueError(
                f"SHAP length mismatch: {len(values)} values vs "
                f"{len(self.feature_names)} feature names"
            )

        return (
            pd.DataFrame({
                "feature": self.feature_names,
                "impact": values
            })
            .sort_values("impact", key=abs, ascending=False)
        )
