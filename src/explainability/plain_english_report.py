"""
AEWS – Plain English Explanation Generator
-----------------------------------------
Converts SHAP feature impacts into readable explanations
for officers and decision-makers.
"""

def generate_explanation(explanation_df, threshold=0.01):
    """
    explanation_df: DataFrame with columns [feature, impact]
    """

    reasons = []

    for _, row in explanation_df.iterrows():
        feature = row["feature"]
        impact = row["impact"]

        if abs(impact) < threshold:
            continue

        if feature == "bio_norm" and impact > 0:
            reasons.append(
                "Biometric update activity is unusually high, increasing authentication pressure."
            )

        elif feature == "demo_norm" and impact > 0:
            reasons.append(
                "Demographic update requests have increased, indicating identity corrections or migration."
            )

        elif feature == "enrol_norm" and impact < 0:
            reasons.append(
                "New enrolment activity is stable, indicating saturation."
            )

        elif feature == "lifecycle_cluster" and impact > 0:
            reasons.append(
                "The district is in a mobile or revalidation-heavy identity lifecycle stage."
            )

    if not reasons:
        return "No dominant stress drivers detected. Identity activity remains stable."

    return " ".join(reasons)
