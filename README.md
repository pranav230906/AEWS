# AEWS: Aadhaar Enrolment and Wellbeing System

A comprehensive data analysis and risk prediction system for Aadhaar identity management, featuring advanced analytics, lifecycle inference, and explainable machine learning insights.

## 📋 Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Notebooks](#project-notebooks)
- [Key Modules](#key-modules)
- [Dashboard](#dashboard)
- [Contributing](#contributing)

## Overview

The AEWS project analyzes Aadhaar enrollment data to:
- Track identity lifecycle patterns and trends
- Calculate Identity Stress Index (ISI) for risk assessment
- Predict potential vulnerabilities and escalation risks
- Provide explainable AI insights through SHAP analysis
- Generate policy recommendations and risk signals

**Data Coverage**: ~2M+ Aadhaar records with demographic, biometric, and enrollment metrics

## Project Structure

```
AEWS/
├── data/                          # Raw and processed datasets
│   ├── raw/                       # Original API data
│   │   ├── biometric/             # Biometric feature data (1.8M records)
│   │   ├── demographic/           # Demographic attributes (2M records)
│   │   └── enrolment/             # Enrollment timestamps (1M records)
│   └── processed/                 # Cleaned and engineered features
│
├── notebooks/                     # Jupyter notebooks for analysis
│   ├── 01_data_ingestion.ipynb    # Data loading and exploration
│   ├── 02_data_cleaning.ipynb     # Data quality and preprocessing
│   ├── 03_feature_engineering.ipynb
│   ├── 04_identity_stress_index.ipynb
│   ├── 05_lifecycle_inference.ipynb
│   ├── 06_risk_prediction_model.ipynb
│   └── 07_explainability_shap.ipynb
│
├── src/                           # Core analytics modules
│   ├── analysis/                  # Risk and escalation analysis
│   ├── data/                      # Data loading and cleaning
│   ├── explainability/            # SHAP and interpretability
│   ├── features/                  # Feature engineering
│   ├── metrics/                   # KPI calculations (ISI, etc.)
│   ├── models/                    # ML models (clustering, classification)
│   ├── policy/                    # Policy engine for recommendations
│   ├── simulator/                 # Resource impact simulation
│   └── visuals/                   # Visualization utilities
│
├── dashboard/                     # Streamlit interactive dashboard
│   ├── app.py                     # Main dashboard application
│   ├── pdf_report.py              # PDF report generation
│   └── state_cleaning.py          # Data state management
│
├── outputs/                       # Generated outputs
│   ├── predictions/               # Risk signals and predictions
│   ├── reports/                   # Generated reports
│   └── visuals/                   # Interactive visualizations
│
└── requirements.txt               # Python dependencies
```

## Features

### 📊 Data Analytics
- Multi-source data ingestion (biometric, demographic, enrollment)
- Advanced data cleaning and validation
- Time-series feature engineering
- Lifecycle pattern detection

### 🔍 Risk Assessment
- **Identity Stress Index (ISI)**: Custom metric for identity vulnerability
- **Escalation Detection**: Identifies high-risk enrollment anomalies
- **Risk Prediction**: ML-based risk classification
- **Lifecycle Clustering**: Segments users by enrollment journey patterns

### 🤖 Machine Learning
- Supervised and unsupervised learning models
- SHAP-based explainability analysis
- Feature importance ranking
- Lifecycle policy engine

### 📈 Visualization & Reporting
- Interactive Streamlit dashboard
- Sankey diagrams for lifecycle flows
- Heat maps for ISI trends
- Automated PDF report generation
- Plain-English policy recommendations

## Installation

### Prerequisites
- Python 3.8+
- pip or conda

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd AEWS
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/Scripts/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Run the Interactive Dashboard
```bash
streamlit run dashboard/app.py
```
The dashboard provides interactive exploration of risk signals, lifecycle patterns, and ISI trends.

### Execute Analysis Notebooks
Open and run notebooks in sequence:
1. `01_data_ingestion.ipynb` - Load and explore raw data
2. `02_data_cleaning.ipynb` - Data preprocessing
3. `03_feature_engineering.ipynb` - Create derived features
4. `04_identity_stress_index.ipynb` - Calculate ISI metrics
5. `05_lifecycle_inference.ipynb` - Clustering and lifecycle analysis
6. `06_risk_prediction_model.ipynb` - Train risk prediction models
7. `07_explainability_shap.ipynb` - SHAP analysis and interpretability

### Generate Reports
```python
from dashboard.pdf_report import generate_report
generate_report(output_path='outputs/reports/report.pdf')
```

## Project Notebooks

| Notebook | Purpose |
|----------|---------|
| 01_data_ingestion | Loads and validates Aadhaar dataset from raw sources |
| 02_data_cleaning | Handles missing values, outliers, and data quality issues |
| 03_feature_engineering | Creates time-series and aggregate features |
| 04_identity_stress_index | Develops ISI metric and calculates risk scores |
| 05_lifecycle_inference | Clusters users into lifecycle segments |
| 06_risk_prediction_model | Trains and evaluates classification models |
| 07_explainability_shap | Explains model predictions with SHAP values |

## Key Modules

### `src.metrics.identity_stress_index`
Calculates Identity Stress Index based on:
- Enrollment anomalies
- Biometric inconsistencies
- Demographic flag patterns

### `src.models.lifecycle_clustering`
Segments enrollment journeys into distinct lifecycle patterns using clustering algorithms.

### `src.models.risk_classifier`
Predicts escalation risk and vulnerability scores using supervised learning.

### `src.analysis.escalation_detector`
Detects anomalous enrollment patterns and high-risk signals.

### `src.explainability`
- `stress_driver_analyzer.py` - Analyzes factors driving ISI
- `plain_english_report.py` - Generates human-readable insights

### `src.visuals`
- `isi_heatmap.py` - Temporal ISI trends
- `lifecycle_curves.py` - Lifecycle progression visualization
- `sankey_builder.py` - Flow diagrams for enrollment patterns

## Dashboard

The Streamlit dashboard (`dashboard/app.py`) provides:
- Real-time risk signal exploration
- Interactive filtering and drill-down
- Lifecycle flow visualization
- ISI trend analysis
- Automated PDF report export

**Launch**: `streamlit run dashboard/app.py`

## Data Specifications

### Raw Data
- **Biometric**: ~1.8M records, feature vectors from 500K-1.5M+ record ranges
- **Demographic**: ~2M records, attributes across multiple batches
- **Enrollment**: ~1M enrollment events with timestamps

### Processed Data
- `biometric_features.csv` - Engineered biometric metrics
- `demographic_monthly.csv` - Monthly demographic aggregates
- `biometric_monthly.csv` - Monthly biometric trends
- `enrolment_monthly.csv` - Monthly enrollment statistics
- `isi_scores.csv` - Calculated Identity Stress Index scores
- `lifecycle_clusters.csv` - Lifecycle segment assignments

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Commit changes: `git commit -m 'Add feature'`
3. Push to branch: `git push origin feature/your-feature`
4. Open a pull request


## Contact

For questions or collaborations, please reach out to the project maintainers.

---

**Last Updated**: January 2026
