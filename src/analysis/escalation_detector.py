# src/analysis/escalation_detector.py

import pandas as pd


def detect_risk_escalation(pred_df):
    """
    Detects risk escalation by comparing current vs previous month
    """

    df = pred_df.copy()

    # Sort for safety
    df = df.sort_values(["state", "district", "year_month"])

    # Previous month risk
    df["prev_risk"] = (
        df.groupby(["state", "district"])["predicted_risk_next"]
        .shift(1)
    )

    # Escalation label
    def escalation_label(row):
        if pd.isna(row["prev_risk"]):
            return "No History"

        if row["prev_risk"] < row["predicted_risk_next"]:
            if row["prev_risk"] == 1 and row["predicted_risk_next"] == 2:
                return "⬆️ Escalated to High"
            return "⬆️ Risk Increased"

        if row["prev_risk"] > row["predicted_risk_next"]:
            return "⬇️ Risk Reduced"

        if row["predicted_risk_next"] == 2:
            return "⚠️ Persistent High"

        return "No Change"

    df["escalation_status"] = df.apply(escalation_label, axis=1)

    return df
