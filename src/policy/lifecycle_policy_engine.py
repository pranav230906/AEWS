# src/policy/lifecycle_policy_engine.py

import pandas as pd

# --------------------------------------------
# Lifecycle cluster → name mapping
# --------------------------------------------
LIFECYCLE_NAME_MAP = {
    0: "Birth–Early Childhood",
    1: "Education Phase",
    2: "Workforce Entry",
    3: "Migration & Mobility",
    4: "Aging & Revalidation"
}

# --------------------------------------------
# Lifecycle → Policy & SDG mapping
# --------------------------------------------
LIFECYCLE_POLICY_MAP = {
    "Birth–Early Childhood": {
        "policy": "Strengthen birth registration, early childhood care, and pre-school infrastructure.",
        "sdgs": ["SDG 3 – Good Health & Well-being", "SDG 4 – Quality Education"]
    },
    "Education Phase": {
        "policy": "Invest in school infrastructure, digital education access, and student services.",
        "sdgs": ["SDG 4 – Quality Education"]
    },
    "Workforce Entry": {
        "policy": "Enhance skill development programs, employment services, and digital inclusion.",
        "sdgs": ["SDG 8 – Decent Work & Economic Growth"]
    },
    "Migration & Mobility": {
        "policy": "Improve portability of services, urban planning, and migrant support systems.",
        "sdgs": ["SDG 10 – Reduced Inequality", "SDG 11 – Sustainable Cities"]
    },
    "Aging & Revalidation": {
        "policy": "Strengthen healthcare access, elderly welfare, and assisted authentication mechanisms.",
        "sdgs": ["SDG 3 – Good Health & Well-being"]
    }
}


def compute_state_lifecycle_intelligence(lifecycle_df):
    """
    Computes dominant lifecycle stage and policy guidance for each state
    """

    df = lifecycle_df.copy()

    # Map lifecycle cluster to name
    df["lifecycle_stage"] = df["lifecycle_cluster"].map(LIFECYCLE_NAME_MAP)

    # Count lifecycle occurrences per state
    summary = (
        df.groupby(["state", "lifecycle_stage"])
        .size()
        .reset_index(name="count")
    )

    # Identify dominant lifecycle per state
    dominant = (
        summary.sort_values("count", ascending=False)
        .groupby("state")
        .first()
        .reset_index()
    )

    # Attach policy & SDGs
    dominant["policy_recommendation"] = dominant["lifecycle_stage"].apply(
        lambda x: LIFECYCLE_POLICY_MAP[x]["policy"]
    )

    dominant["sdgs"] = dominant["lifecycle_stage"].apply(
        lambda x: ", ".join(LIFECYCLE_POLICY_MAP[x]["sdgs"])
    )

    return dominant
