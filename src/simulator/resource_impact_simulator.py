# src/simulator/resource_impact_simulator.py

import re

# --------------------------------------------------
# Simple controlled-language parser
# --------------------------------------------------
def parse_simulation_query(query: str):
    """
    Extracts quantity, resource type, state, district from query.
    Supported example:
    'What if UIDAI adds 2 biometric operators in Maharashtra Palghar'
    """

    query = query.lower()

    quantity_match = re.search(r"add[s]? (\d+)", query)
    quantity = int(quantity_match.group(1)) if quantity_match else 1

    resource = "biometric" if "biometric" in query else None

    # Very simple heuristic extraction (safe for hackathon)
    tokens = query.split(" in ")
    location = tokens[-1].title() if len(tokens) > 1 else ""

    parts = location.split()
    state = parts[0] if len(parts) > 0 else None
    district = parts[-1] if len(parts) > 1 else None

    return {
        "resource": resource,
        "quantity": quantity,
        "state": state,
        "district": district,
    }


# --------------------------------------------------
# Impact Simulation Logic (Explainable)
# --------------------------------------------------
def simulate_biometric_capacity(
    hist_df,
    additional_operators
):
    """
    Simulates impact of adding biometric operators using
    observed elasticity (rule-based, not ML).
    """

    # Historical averages
    old_isi = hist_df["isi_score"].mean()
    bio = hist_df["bio_norm"].mean()
    demo = hist_df["demo_norm"].mean()
    enrol = hist_df["enrol_norm"].mean()

    # Assumption: each operator reduces biometric pressure by ~9%
    bio_reduction_factor = min(0.09 * additional_operators, 0.4)

    new_bio = max(bio * (1 - bio_reduction_factor), 0)

    # Recompute ISI (same logic as original metric)
    new_isi = (
        0.5 * new_bio +
        0.3 * demo -
        0.2 * enrol
    )

    isi_drop_pct = ((old_isi - new_isi) / old_isi) * 100 if old_isi > 0 else 0

    # Risk downgrade estimation
    if new_isi < 0.6:
        downgrade = "High → Medium very likely (~70%)"
    elif new_isi < 0.7:
        downgrade = "Moderate improvement (~40%)"
    else:
        downgrade = "Limited impact (<20%)"

    return {
        "old_isi": round(old_isi, 3),
        "new_isi": round(new_isi, 3),
        "isi_reduction_pct": round(isi_drop_pct, 1),
        "risk_downgrade": downgrade,
    }
