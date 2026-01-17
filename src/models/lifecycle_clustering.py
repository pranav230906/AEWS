"""
AEWS - Identity Lifecycle Clustering
-----------------------------------
Infers identity lifecycle stages using unsupervised learning.
"""

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


class LifecycleClustering:
    def __init__(self, n_clusters: int = 5, random_state: int = 42):
        """
        n_clusters = number of lifecycle stages
        """
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.scaler = StandardScaler()
        self.model = KMeans(
            n_clusters=n_clusters,
            random_state=random_state,
            n_init=10
        )

    def fit_predict(
        self,
        isi_df: pd.DataFrame,
        feature_cols: list
    ) -> pd.DataFrame:
        """
        Fit clustering model and assign lifecycle stage
        """

        df = isi_df.copy()

        # Scale features
        X = self.scaler.fit_transform(df[feature_cols])

        # Cluster
        df["lifecycle_cluster"] = self.model.fit_predict(X)

        return df
