import os
import sys
import pandas as pd
from sqlalchemy import text

# Setup paths to ensure local imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db import engine
from state_cleaning import clean_state_names

def ingest():
    print("Starting data ingestion...")

    # Load files
    print("Loading CSV files...")
    isi_df = pd.read_csv("data/processed/isi_scores.csv")
    lifecycle_df = pd.read_csv("data/processed/lifecycle_clusters.csv")
    risk_df = pd.read_csv("outputs/predictions/aews_risk_signals.csv")

    # Clean state/district names
    print("Cleaning state/district names...")
    isi_df = clean_state_names(isi_df)
    lifecycle_df = clean_state_names(lifecycle_df)
    risk_df = clean_state_names(risk_df)

    # Drop NaNs / Duplicates in PK columns to ensure database integrity
    print("Handling NaNs and duplicates in PK columns...")
    for df_name, df in [("isi_scores", isi_df), ("lifecycle_clusters", lifecycle_df), ("aews_risk_signals", risk_df)]:
        # Ensure year_month is string type and handle NaT/NaN
        df["year_month"] = df["year_month"].astype(str).str.strip()
        df = df[~df["year_month"].isin(["NaT", "nan", "NaN", ""])]
        df = df.dropna(subset=["state", "district", "year_month"])
        df = df.drop_duplicates(subset=["state", "district", "year_month"])
        
        # Save back to variable
        if df_name == "isi_scores":
            isi_df = df
        elif df_name == "lifecycle_clusters":
            lifecycle_df = df
        elif df_name == "aews_risk_signals":
            risk_df = df

    # Ingest into DB
    print("Writing tables to database...")
    with engine.begin() as connection:
        # We overwrite existing tables
        isi_df.to_sql("isi_scores", con=connection, if_exists="replace", index=False)
        lifecycle_df.to_sql("lifecycle_clusters", con=connection, if_exists="replace", index=False)
        risk_df.to_sql("aews_risk_signals", con=connection, if_exists="replace", index=False)

    print("Creating primary keys and indexes...")
    with engine.begin() as connection:
        # Define primary keys
        connection.execute(text("ALTER TABLE isi_scores ADD PRIMARY KEY (state, district, year_month);"))
        connection.execute(text("ALTER TABLE lifecycle_clusters ADD PRIMARY KEY (state, district, year_month);"))
        connection.execute(text("ALTER TABLE aews_risk_signals ADD PRIMARY KEY (state, district, year_month);"))

        # Define indexes
        connection.execute(text("CREATE INDEX IF NOT EXISTS idx_isi_state_district ON isi_scores(state, district);"))
        connection.execute(text("CREATE INDEX IF NOT EXISTS idx_lifecycle_state ON lifecycle_clusters(state);"))
        connection.execute(text("CREATE INDEX IF NOT EXISTS idx_risk_year_month ON aews_risk_signals(year_month);"))

    print("Ingestion complete and tables successfully indexed!")

if __name__ == "__main__":
    ingest()
