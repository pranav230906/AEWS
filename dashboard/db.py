import os
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from dashboard.config import settings

# Create the Engine with connection pooling
engine = create_engine(settings.DATABASE_URL, pool_size=5, max_overflow=10)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Define the Schema
class GeneratedReport(Base):
    __tablename__ = "generated_reports"

    id = Column(Integer, primary_key=True, index=True)
    state = Column(String, index=True)
    district = Column(String, index=True)
    risk_level = Column(String)
    generation_date = Column(DateTime, default=datetime.utcnow)
    file_path = Column(String)

class ISIScore(Base):
    __tablename__ = "isi_scores"

    state = Column(String, primary_key=True)
    district = Column(String, primary_key=True)
    year_month = Column(String, primary_key=True)
    enrol_activity = Column(Integer)
    demo_activity = Column(Integer)
    bio_activity = Column(Integer)
    enrol_norm = Column(Float)
    demo_norm = Column(Float)
    bio_norm = Column(Float)
    isi_score = Column(Float)

class LifecycleCluster(Base):
    __tablename__ = "lifecycle_clusters"

    state = Column(String, primary_key=True)
    district = Column(String, primary_key=True)
    year_month = Column(String, primary_key=True)
    enrol_activity = Column(Integer)
    demo_activity = Column(Integer)
    bio_activity = Column(Integer)
    enrol_norm = Column(Float)
    demo_norm = Column(Float)
    bio_norm = Column(Float)
    isi_score = Column(Float)
    lifecycle_cluster = Column(Integer)

class AEWSRiskSignal(Base):
    __tablename__ = "aews_risk_signals"

    state = Column(String, primary_key=True)
    district = Column(String, primary_key=True)
    year_month = Column(String, primary_key=True)
    predicted_risk_next = Column(Integer)

# Initialize Database (Creates tables if they don't exist and seeds them if empty)
def init_db():
    Base.metadata.create_all(bind=engine)
    
    # Check if database is empty by checking the count of risk signals
    try:
        with engine.connect() as conn:
            res = conn.execute(text("SELECT COUNT(*) FROM aews_risk_signals"))
            count = res.scalar()
    except Exception:
        count = 0

    if count == 0:
        print("Database is empty. Seeding from local CSV files...")
        from state_cleaning import clean_state_names
        
        DB_DIR = os.path.dirname(os.path.abspath(__file__))
        PROJECT_ROOT = os.path.abspath(os.path.join(DB_DIR, ".."))

        try:
            # 1. Seed isi_scores
            isi_path = os.path.join(PROJECT_ROOT, "data", "processed", "isi_scores.csv")
            if os.path.exists(isi_path):
                df = pd.read_csv(isi_path)
                df = clean_state_names(df)
                # Match table schema columns
                cols = ["state", "district", "year_month", "enrol_activity", "demo_activity", 
                        "bio_activity", "enrol_norm", "demo_norm", "bio_norm", "isi_score"]
                df = df[[c for c in cols if c in df.columns]]
                df.to_sql("isi_scores", con=engine, if_exists="append", index=False)
                print("Seeded 'isi_scores' table successfully.")

            # 2. Seed lifecycle_clusters
            lifecycle_path = os.path.join(PROJECT_ROOT, "data", "processed", "lifecycle_clusters.csv")
            if os.path.exists(lifecycle_path):
                df = pd.read_csv(lifecycle_path)
                df = clean_state_names(df)
                cols = ["state", "district", "year_month", "enrol_activity", "demo_activity", 
                        "bio_activity", "enrol_norm", "demo_norm", "bio_norm", "isi_score", "lifecycle_cluster"]
                df = df[[c for c in cols if c in df.columns]]
                df.to_sql("lifecycle_clusters", con=engine, if_exists="append", index=False)
                print("Seeded 'lifecycle_clusters' table successfully.")

            # 3. Seed aews_risk_signals
            risk_path = os.path.join(PROJECT_ROOT, "outputs", "predictions", "aews_risk_signals.csv")
            if os.path.exists(risk_path):
                df = pd.read_csv(risk_path)
                df = clean_state_names(df)
                cols = ["state", "district", "year_month", "predicted_risk_next"]
                df = df[[c for c in cols if c in df.columns]]
                df.to_sql("aews_risk_signals", con=engine, if_exists="append", index=False)
                print("Seeded 'aews_risk_signals' table successfully.")
        except Exception:
            print("Error seeding database: A database operation failure occurred.")

# Save Report Function
def save_report_to_db(state: str, district: str, risk_level: str, file_path: str):
    db = SessionLocal()
    try:
        new_report = GeneratedReport(
            state=state,
            district=district,
            risk_level=risk_level,
            file_path=file_path
        )
        db.add(new_report)
        db.commit()
    except Exception:
        db.rollback()
        print("Error saving report to PostgreSQL: A database transaction failure occurred.")
    finally:
        db.close() # Returns connection to the pool

# Retrieve Past Reports
def get_past_reports(state: str, district: str) -> pd.DataFrame:
    query = text("""
        SELECT generation_date, risk_level, file_path 
        FROM generated_reports 
        WHERE state = :state AND district = :district 
        ORDER BY generation_date DESC
    """)
    df = pd.read_sql(
        query, 
        con=engine, 
        params={"state": state, "district": district}
    )
    return df

# Helper to load dashboard alert signals for the latest month
def get_latest_alerts() -> tuple:
    with engine.connect() as conn:
        res = conn.execute(text("SELECT MAX(year_month) FROM aews_risk_signals"))
        latest_month = res.scalar()
    
    if not latest_month:
        return pd.DataFrame(), None

    query = text("""
        WITH prev_risk_cte AS (
            SELECT 
                state, 
                district, 
                year_month, 
                predicted_risk_next,
                LAG(predicted_risk_next) OVER (
                    PARTITION BY state, district 
                    ORDER BY year_month
                ) as prev_risk
            FROM aews_risk_signals
        )
        SELECT state, district, year_month, predicted_risk_next, prev_risk
        FROM prev_risk_cte
        WHERE year_month = :latest_month
    """)
    
    alerts_df = pd.read_sql(query, con=engine, params={"latest_month": latest_month})
    
    avg_query = text("""
        SELECT state, district, AVG(bio_norm) as bio_norm_avg, AVG(demo_norm) as demo_norm_avg
        FROM isi_scores
        GROUP BY state, district
    """)
    avg_df = pd.read_sql(avg_query, con=engine)
    
    alerts_df = pd.merge(alerts_df, avg_df, on=["state", "district"], how="left")
    return alerts_df, latest_month

# Helper to get detail page metrics
def get_district_history(state: str, district: str) -> pd.DataFrame:
    query = text("""
        SELECT year_month, enrol_activity, demo_activity, bio_activity, enrol_norm, demo_norm, bio_norm, isi_score
        FROM isi_scores
        WHERE state = :state AND district = :district
        ORDER BY year_month
    """)
    return pd.read_sql(query, con=engine, params={"state": state, "district": district})

# Helper to retrieve lifecycle data for a given state
def get_state_lifecycle_data(state: str) -> pd.DataFrame:
    query = text("""
        SELECT state, lifecycle_cluster
        FROM lifecycle_clusters
        WHERE state = :state
    """)
    return pd.read_sql(query, con=engine, params={"state": state})

# Helper to load simulator history
def get_simulator_data(state_pattern: str, district_pattern: str) -> pd.DataFrame:
    query = text("""
        SELECT enrol_activity, demo_activity, bio_activity, enrol_norm, demo_norm, bio_norm, isi_score
        FROM isi_scores
        WHERE state ILIKE :state AND district ILIKE :district
        ORDER BY year_month
    """)
    return pd.read_sql(
        query, 
        con=engine, 
        params={"state": f"%{state_pattern}%", "district": f"%{district_pattern}%"}
    )
