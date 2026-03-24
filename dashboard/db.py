import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "outputs", "reports.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS generated_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            state TEXT,
            district TEXT,
            risk_level TEXT,
            generation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            file_path TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_report_to_db(state, district, risk_level, file_path):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO generated_reports (state, district, risk_level, file_path)
        VALUES (?, ?, ?, ?)
    ''', (state, district, risk_level, file_path))
    conn.commit()
    conn.close()

def get_past_reports(state, district):
    conn = sqlite3.connect(DB_PATH)
    import pandas as pd
    query = "SELECT generation_date, risk_level, file_path FROM generated_reports WHERE state = ? AND district = ? ORDER BY generation_date DESC"
    df = pd.read_sql_query(query, conn, params=(state, district))
    conn.close()
    return df
