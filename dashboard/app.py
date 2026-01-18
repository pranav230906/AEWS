# =========================================================
# Windows-safe import setup (VERY IMPORTANT)
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
    "Early warning, escalation detection, policy intelligence & decision simulation"
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
# Clean State Names
# =========================================================
isi_df = clean_state_names(isi_df)
lifecycle_df = clean_state_names(lifecycle_df)
pred_df = clean_state_names(pred_df)

# =========================================================
# Escalation Detection
# =========================================================
pred_df = detect_risk_escalation(pred_df)

# =========================================================
# Latest Month Filter
# =========================================================
latest_month = pred_df["year_month"].max()
alerts_df = pred_df[pred_df["year_month"] == latest_month].copy()

risk_map = {0: "🟢 Low", 1: "🟡 Medium", 2: "🔴 High"}
alerts_df["Risk Level"] = alerts_df["predicted_risk_next"].map(risk_map)

# =========================================================
# Recommendation Summary (table-level)
# =========================================================
def recommendation_summary(row):
    subset = isi_df[
        (isi_df["state"] == row["state"]) &
        (isi_df["district"] == row["district"])
    ]

    if subset.empty:
        return "Monitor"

    bio = subset["bio_norm"].mean()
    demo = subset["demo_norm"].mean()

    if row["predicted_risk_next"] == 2:
        return "Increase biometric capacity" if bio >= demo else "Deploy update camps"
    elif row["predicted_risk_next"] == 1:
        return "Monitor & prepare"
    else:
        return "No action required"

alerts_df["Recommended Action"] = alerts_df.apply(
    recommendation_summary, axis=1
)

# =========================================================
# Population Lifecycle Intelligence (State-wise)
# =========================================================
pli_df = compute_state_lifecycle_intelligence(lifecycle_df)

# =========================================================
# Tabs
# =========================================================
tab_alerts, tab_analysis, tab_simulator = st.tabs(
    [
        "🚦 National Risk Alerts",
        "🔍 State & District Analysis",
        "🧪 Resource Impact Simulator"
    ]
)

# =========================================================
# TAB 1: NATIONAL RISK ALERTS
# =========================================================
with tab_alerts:

    st.subheader("📊 National Risk Distribution (Next Month)")

    risk_counts = alerts_df["predicted_risk_next"].value_counts().sort_index()
    labels = ["Low", "Medium", "High"]
    values = [
        risk_counts.get(0, 0),
        risk_counts.get(1, 0),
        risk_counts.get(2, 0)
    ]

    fig_nat, ax_nat = plt.subplots()
    ax_nat.bar(labels, values, color=["green", "gold", "red"])
    ax_nat.set_ylabel("Number of Districts")
    ax_nat.set_title("Next-Month Aadhaar Service Risk Distribution")
    st.pyplot(fig_nat)

    # ---------------- Escalation Alerts ----------------
    st.subheader("🚨 Escalation Alerts (Compared to Last Month)")

    escalated = alerts_df[
        alerts_df["escalation_status"].str.contains("Escalated")
    ]

    if escalated.empty:
        st.success("No districts escalated to higher risk this month.")
    else:
        st.dataframe(
            escalated[
                ["state", "district", "Risk Level", "escalation_status", "Recommended Action"]
            ].sort_values(["state", "district"]),
            use_container_width=True
        )

    # ---------------- Risk Tabs ----------------
    tab_high, tab_medium, tab_low = st.tabs(
        ["🔴 High Risk", "🟡 Medium Risk", "🟢 Low Risk"]
    )

    for risk_val, tab in [(2, tab_high), (1, tab_medium), (0, tab_low)]:
        with tab:
            df = alerts_df[alerts_df["predicted_risk_next"] == risk_val]
            st.dataframe(
                df[
                    ["state", "district", "Risk Level", "escalation_status", "Recommended Action"]
                ].sort_values(["state", "district"]),
                use_container_width=True
            )

# =========================================================
# TAB 2: STATE & DISTRICT ANALYSIS
# =========================================================
with tab_analysis:

    st.subheader("🔎 State & District Risk Analysis")

    selected_state = st.selectbox(
        "Select State", sorted(alerts_df["state"].unique())
    )

    state_df = alerts_df[alerts_df["state"] == selected_state]

    selected_district = st.selectbox(
        "Select District", sorted(state_df["district"].unique())
    )

    alert_row = state_df[state_df["district"] == selected_district].iloc[0]
    risk_level = alert_row["predicted_risk_next"]

    st.markdown(
        f"### {selected_state} → {selected_district} : "
        f"**{risk_map[risk_level]} Risk Next Month**"
    )
    st.markdown(f"**Risk Change:** {alert_row['escalation_status']}")

    hist_df = isi_df[
        (isi_df["state"] == selected_state) &
        (isi_df["district"] == selected_district)
    ]

    bio_mean = hist_df["bio_norm"].mean()
    demo_mean = hist_df["demo_norm"].mean()
    enrol_mean = hist_df["enrol_norm"].mean()

    # ---------------- WHY ----------------
    st.subheader("🧠 Why is this area at risk?")

    reasons = []
    if bio_mean > 0.6:
        reasons.append("High biometric update activity increasing authentication load.")
    if demo_mean > 0.5:
        reasons.append("Demographic update surge indicating migration or corrections.")
    if enrol_mean < 0.2:
        reasons.append("Enrolment saturation shifting load to updates.")
    if not reasons:
        reasons.append("No dominant stress drivers detected.")

    for r in reasons:
        st.write("•", r)

    # ---------------- Stress Drivers ----------------
    st.subheader("📊 Stress Driver Contribution")

    driver_df = pd.DataFrame({
        "Driver": ["Biometric", "Demographic", "Enrolment"],
        "Intensity": [bio_mean, demo_mean, enrol_mean]
    })

    fig_drv, ax_drv = plt.subplots()
    ax_drv.barh(driver_df["Driver"], driver_df["Intensity"])
    st.pyplot(fig_drv)

    # ---------------- ISI Trend ----------------
    st.subheader("📈 Identity Stress Trend (District)")

    trend = hist_df.groupby("year_month")["isi_score"].mean().reset_index()
    fig_tr, ax_tr = plt.subplots()
    ax_tr.plot(trend["year_month"], trend["isi_score"], marker="o")
    plt.xticks(rotation=45)
    st.pyplot(fig_tr)

    # ---------------- District Heatmap ----------------
    st.subheader("🌍 District Stress Heatmap (State Level)")

    state_hist = isi_df[isi_df["state"] == selected_state]
    heatmap_df = state_hist.pivot(
        index="district", columns="year_month", values="isi_score"
    )

    fig_hm, ax_hm = plt.subplots(figsize=(10, 6))
    ax_hm.imshow(heatmap_df.fillna(0), aspect="auto", cmap="Reds")
    ax_hm.set_ylabel("District")
    ax_hm.set_xlabel("Month")
    st.pyplot(fig_hm)

    # ---------------- Lifecycle Persistence ----------------
    st.subheader("🔁 Identity Lifecycle Persistence (State)")

    lifecycle_state = lifecycle_df[lifecycle_df["state"] == selected_state]
    lifecycle_summary = (
        lifecycle_state.groupby("lifecycle_cluster")
        .size()
        .reset_index(name="Observed Months")
        .sort_values("Observed Months", ascending=False)
    )
    st.dataframe(lifecycle_summary, use_container_width=True)

    # ---------------- Population Lifecycle Intelligence ----------------
    st.subheader("🧬 Population Lifecycle Intelligence (State-Level)")

    state_pli = pli_df[pli_df["state"] == selected_state]
    if not state_pli.empty:
        row = state_pli.iloc[0]
        st.markdown(
            f"""
            **Dominant Lifecycle Stage:**  
            🔹 **{row['lifecycle_stage']}**

            **Policy Recommendation:**  
            {row['policy_recommendation']}

            **Relevant SDGs:**  
            {row['sdgs']}
            """
        )

    # ---------------- Recommendations ----------------
    st.subheader("🛠️ Recommended Actions")

    actions = (
        ["Deploy iris scanners and biometric operators", "Extend Aadhaar centre hours"]
        if risk_level == 2 and bio_mean >= demo_mean else
        ["Organize demographic update camps", "Increase correction staff"]
        if risk_level == 2 else
        ["Monitor trends", "Prepare standby staff"]
        if risk_level == 1 else
        ["Continue routine operations"]
    )

    for a in actions:
        st.write("•", a)

    # ---------------- PDF Report ----------------
    st.subheader("⬇️ Download District Report (PDF)")

    pdf_path = f"outputs/reports/{selected_state}_{selected_district}_AEWS_Report.pdf"

    generate_pdf_report(
        state=selected_state,
        district=selected_district,
        risk_level=risk_map[risk_level],
        reasons=reasons,
        actions=actions,
        output_path=pdf_path
    )

    with open(pdf_path, "rb") as f:
        st.download_button(
            "Download PDF Report",
            f,
            file_name=os.path.basename(pdf_path),
            mime="application/pdf"
        )

# =========================================================
# TAB 3: RESOURCE IMPACT SIMULATOR (CHAT UI)
# =========================================================
with tab_simulator:

    st.subheader("🧪 Resource Impact Simulator")
    st.caption(
        "Simulate the likely impact of UIDAI resource allocation decisions"
    )

    query = st.text_input(
        "Ask a what-if question",
        placeholder="What if UIDAI adds 2 biometric operators in Maharashtra Palghar?"
    )

    if st.button("Simulate Impact") and query:
        parsed = parse_simulation_query(query)

        if parsed["resource"] != "biometric":
            st.warning("Currently only biometric operator simulations are supported.")
        else:
            hist_df = isi_df[
                (isi_df["state"].str.contains(parsed["state"], case=False, na=False)) &
                (isi_df["district"].str.contains(parsed["district"], case=False, na=False))
            ]

            if hist_df.empty:
                st.error("No historical data found for the specified location.")
            else:
                result = simulate_biometric_capacity(
                    hist_df,
                    parsed["quantity"]
                )

                st.success("Simulation Result (Indicative)")

                st.markdown(
                    f"""
                    **Location:** {parsed['state']} → {parsed['district']}  
                    **Resource Added:** {parsed['quantity']} biometric operators  

                    **Estimated ISI Reduction:** {result['isi_reduction_pct']}%  
                    **ISI (Before → After):** {result['old_isi']} → {result['new_isi']}  
                    **Risk Impact:** {result['risk_downgrade']}

                    **Interpretation:**  
                    Increasing biometric capacity reduces authentication pressure
                    and can help downgrade service stress if sustained.
                    """
                )

                st.info(
                    "⚠️ This is a scenario simulation based on historical elasticities, "
                    "not a deterministic prediction."
                )
