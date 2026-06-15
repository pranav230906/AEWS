import os
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, DateTime, text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Get the database URL from the environment variable
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("No DATABASE_URL found in environment variables. Check your .env file.")

# Create the Engine with connection pooling
engine = create_engine(DATABASE_URL, pool_size=5, max_overflow=10)
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

# Initialize Database (Creates tables if they don't exist)
def init_db():
    Base.metadata.create_all(bind=engine)

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
    except Exception as e:
        db.rollback()
        print(f"Error saving report to PostgreSQL: {e}")
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
    # Use pandas to read directly from the SQLAlchemy engine
    df = pd.read_sql(
        query, 
        con=engine, 
        params={"state": state, "district": district}
    )
    return df
