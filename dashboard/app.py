# =========================================================
# Windows-safe import setup
# =========================================================
import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# =========================================================
# Imports
# =========================================================
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from state_cleaning import clean_state_names
from pdf_report import generate_pdf_report

from src.analysis.escalation_detector import detect_risk_escalation
from src.policy.lifecycle_policy_engine import compute_state_lifecycle_intelligence
from src.simulator.resource_impact_simulator import (
    parse_simulation_query,
    simulate_biometric_capacity
)

# =========================================================
# Page Config
# =========================================================
st.set_page_config(
    page_title="AEWS – Aadhaar Early Warning System",
    layout="wide"
)

st.title("🚨 AEWS – Aadhaar Early Warning System")
st.caption(
    "Early warning, escalation detection, policy intelligence, and decision simulation for Aadhaar services"
)

# =========================================================
# Load Data
# =========================================================
@st.cache_data
def load_data():
    isi_df = pd.read_csv("data/processed/isi_scores.csv")
    lifecycle_df = pd.read_csv("data/processed/lifecycle_clusters.csv")
    pred_df = pd.read_csv("outputs/predictions/aews_risk_signals.csv")
    return isi_df, lifecycle_df, pred_df

isi_df, lifecycle_df, pred_df = load_data()

# =========================================================
# Cleaning & Processing
# =========================================================
isi_df = clean_state_names(isi_df)
lifecycle_df = clean_state_names(lifecycle_df)
pred_df = clean_state_names(pred_df)

pred_df = detect_risk_escalation(pred_df)

latest_month = pred_df["year_month"].max()
alerts_df = pred_df[pred_df["year_month"] == latest_month].copy()

risk_map = {0: "🟢 Low", 1: "🟡 Medium", 2: "🔴 High"}
alerts_df["Risk Level"] = alerts_df["predicted_risk_next"].map(risk_map)

# =========================================================
# Recommended Action
# =========================================================
def compute_recommended_action(row):
    subset = isi_df[
        (isi_df["state"] == row["state"]) &
        (isi_df["district"] == row["district"])
    ]

    if subset.empty:
        return "Monitor"

    bio = subset["bio_norm"].mean()
    demo = subset["demo_norm"].mean()

    if row["predicted_risk_next"] == 2:
        return (
            "Increase biometric capacity / deploy iris scanners"
            if bio >= demo
            else "Organize demographic update camps"
        )
    elif row["predicted_risk_next"] == 1:
        return "Monitor trends and prepare standby staff"
    else:
        return "No immediate action required"


alerts_df["Recommended Action"] = alerts_df.apply(
    compute_recommended_action, axis=1
)

pli_df = compute_state_lifecycle_intelligence(lifecycle_df)

# =========================================================
# Tabs
# =========================================================
tab_alerts, tab_analysis, tab_simulator = st.tabs(
    ["🚦 National Risk Alerts", "🔍 State & District Analysis", "🧪 Resource Impact Simulator"]
)

# =========================================================
# TAB 1: NATIONAL RISK ALERTS
# =========================================================
with tab_alerts:

    st.subheader("📊 National Risk Overview")

    col1, col2 = st.columns([1, 1])

    # ---------- Infographic ----------
    with col1:
        st.caption("Distribution of districts by predicted Aadhaar service risk level.")

        risk_counts = alerts_df["predicted_risk_next"].value_counts().sort_index()
        fig, ax = plt.subplots(figsize=(4.5, 3))
        ax.bar(
            ["Low", "Medium", "High"],
            [risk_counts.get(0, 0), risk_counts.get(1, 0), risk_counts.get(2, 0)],
            color=["green", "gold", "red"]
        )
        ax.set_ylabel("District Count")
        st.pyplot(fig)

        st.markdown("**How to read this chart:**")
        st.markdown("- Taller bars indicate more districts under that risk level")
        st.markdown("- Growth in 🔴 High indicates national stress buildup")

    # ---------- Risk Tables ----------
    with col2:
        st.caption("All districts classified by predicted risk level for the next month.")

        tab_high, tab_medium, tab_low = st.tabs(
            ["🔴 High Risk", "🟡 Medium Risk", "🟢 Low Risk"]
        )

        for risk_val, tab in [(2, tab_high), (1, tab_medium), (0, tab_low)]:
            with tab:
                st.dataframe(
                    alerts_df[alerts_df["predicted_risk_next"] == risk_val][
                        ["state", "district", "Risk Level", "Recommended Action"]
                    ].sort_values(["state", "district"]),
                    height=250,
                    use_container_width=True
                )

    # ---------- Escalation Section ----------
    st.subheader("🚨 Risk Escalation Analysis")
    st.caption("Classification of districts based on month-over-month risk change.")

    tab_esc, tab_persist, tab_other = st.tabs(
        ["⬆️ Escalated", "⚠️ Persistent High", "➖ No Change / Reduced"]
    )

    with tab_esc:
        st.dataframe(
            alerts_df[
                alerts_df["escalation_status"].str.contains("Escalated")
            ][
                ["state", "district", "Risk Level", "escalation_status", "Recommended Action"]
            ],
            height=250,
            use_container_width=True
        )

    with tab_persist:
        st.dataframe(
            alerts_df[
                alerts_df["escalation_status"].str.contains("Persistent")
            ][
                ["state", "district", "Risk Level", "escalation_status", "Recommended Action"]
            ],
            height=250,
            use_container_width=True
        )

    with tab_other:
        st.dataframe(
            alerts_df[
                alerts_df["escalation_status"].isin(["No Change", "⬇️ Risk Reduced"])
            ][
                ["state", "district", "Risk Level", "escalation_status", "Recommended Action"]
            ],
            height=250,
            use_container_width=True
        )

    st.info(
        "🧠 **Signals Explained:**  \n"
        "⬆️ Escalated → Situation worsening, act early  \n"
        "⚠️ Persistent High → Structural pressure remains  \n"
        "➖ No Change / Reduced → Situation stable or improving"
    )

    st.markdown(
        "**Features used:** Risk prediction model, Identity Stress Index (ISI), "
        "and month-over-month escalation detection."
    )

# =========================================================
# TAB 2: STATE & DISTRICT ANALYSIS
# =========================================================
with tab_analysis:

    st.subheader("🔍 State & District Risk Analysis")
    st.caption("Why a district is under stress and what actions are recommended.")

    c1, c2 = st.columns([1, 1])

    with c1:
        selected_state = st.selectbox("Select State", sorted(alerts_df["state"].unique()))
    with c2:
        selected_district = st.selectbox(
            "Select District",
            sorted(alerts_df[alerts_df["state"] == selected_state]["district"].unique())
        )

    alert_row = alerts_df[
        (alerts_df["state"] == selected_state) &
        (alerts_df["district"] == selected_district)
    ].iloc[0]

    risk_level = alert_row["predicted_risk_next"]

    st.markdown(
        f"### {selected_state} → {selected_district} | **{risk_map[risk_level]} Risk**"
    )
    st.markdown(f"**Risk Change:** {alert_row['escalation_status']}")

    hist_df = isi_df[
        (isi_df["state"] == selected_state) &
        (isi_df["district"] == selected_district)
    ]

    bio, demo, enrol = (
        hist_df["bio_norm"].mean(),
        hist_df["demo_norm"].mean(),
        hist_df["enrol_norm"].mean()
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        st.caption("Relative contribution of identity activities to stress.")

        fig, ax = plt.subplots(figsize=(4.5, 3))
        ax.barh(["Biometric", "Demographic", "Enrolment"], [bio, demo, enrol])
        st.pyplot(fig)

    with col2:
        st.caption("Trend of Identity Stress Index (ISI) over time.")

        trend = hist_df.groupby("year_month")["isi_score"].mean().reset_index()
        fig, ax = plt.subplots(figsize=(4.5, 3))
        ax.plot(trend["year_month"], trend["isi_score"], marker="o")
        ax.tick_params(axis="x", rotation=45)
        st.pyplot(fig)

    st.subheader("🧬 Population Lifecycle Intelligence (State-Level)")
    st.caption("Policy-relevant insight derived from dominant identity lifecycle patterns.")

    state_pli = pli_df[pli_df["state"] == selected_state]
    if not state_pli.empty:
        row = state_pli.iloc[0]
        st.markdown(f"**Dominant Lifecycle Stage:** {row['lifecycle_stage']}")
        st.markdown(f"**Policy Recommendation:** {row['policy_recommendation']}")
        st.markdown(f"**Relevant SDGs:** {row['sdgs']}")

    st.info(
        "🧠 This tab explains WHY stress occurs, WHICH activity dominates, "
        "and WHAT operational and policy actions are suitable."
    )

# =========================================================
# TAB 3: RESOURCE IMPACT SIMULATOR
# =========================================================
with tab_simulator:

    st.subheader("🧪 Resource Impact Simulator")
    st.caption("Simulate how adding resources may reduce Aadhaar service stress.")

    query = st.text_input(
        "Ask a what-if question",
        placeholder="What if UIDAI adds 2 biometric operators in Maharashtra Palghar?"
    )

    if st.button("Simulate") and query:
        parsed = parse_simulation_query(query)

        hist_df = isi_df[
            (isi_df["state"].str.contains(parsed["state"], case=False, na=False)) &
            (isi_df["district"].str.contains(parsed["district"], case=False, na=False))
        ]

        if hist_df.empty:
            st.error("No historical data found for the specified location.")
        else:
            result = simulate_biometric_capacity(hist_df, parsed["quantity"])

            col1, col2 = st.columns([1, 1])

            with col1:
                st.markdown(f"**Estimated ISI Reduction:** {result['isi_reduction_pct']}%")
                st.markdown(f"**ISI Before → After:** {result['old_isi']} → {result['new_isi']}")

            with col2:
                st.markdown(f"**Risk Impact:** {result['risk_downgrade']}")

            st.info(
                "⚠️ Scenario simulation based on historical elasticities, "
                "not a deterministic forecast."
            )
