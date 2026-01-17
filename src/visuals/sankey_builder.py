import plotly.graph_objects as go
import pandas as pd


def build_lifecycle_sankey(df):
    """
    AEWS Sankey:
    Identity Lifecycle Stage  →  Next-Month Risk Level
    """

    # -----------------------------
    # Define readable labels
    # -----------------------------
    lifecycle_labels = {
        0: "Stable Identity",
        1: "Growing Identity",
        2: "Mobile Identity",
        3: "Revalidating Identity",
        4: "High-Churn Identity"
    }

    risk_labels = {
        0: "🟢 Low Stress",
        1: "🟡 Medium Stress",
        2: "🔴 High Stress"
    }

    # -----------------------------
    # Prepare flow data
    # -----------------------------
    flow_df = (
        df.groupby(["lifecycle_cluster", "risk_label_next"])
          .size()
          .reset_index(name="count")
    )

    # -----------------------------
    # Build node list
    # -----------------------------
    lifecycle_nodes = list(lifecycle_labels.values())
    risk_nodes = list(risk_labels.values())

    labels = lifecycle_nodes + risk_nodes

    # Node index mapping
    lifecycle_index = {k: i for i, k in enumerate(lifecycle_labels.keys())}
    risk_index = {
        k: i + len(lifecycle_nodes)
        for i, k in enumerate(risk_labels.keys())
    }

    # -----------------------------
    # Build links
    # -----------------------------
    sources = flow_df["lifecycle_cluster"].map(lifecycle_index)
    targets = flow_df["risk_label_next"].map(risk_index)
    values = flow_df["count"]

    # -----------------------------
    # Color scheme (meaningful)
    # -----------------------------
    node_colors = [
        "#4CAF50",  # Stable - green
        "#81C784",  # Growing - light green
        "#64B5F6",  # Mobile - blue
        "#FFB74D",  # Revalidating - orange
        "#E57373",  # High churn - red
        "#81C784",  # Low stress
        "#FFD54F",  # Medium stress
        "#E53935"   # High stress
    ]

    link_colors = [
        "rgba(100,181,246,0.4)" if r == 0 else
        "rgba(255,213,79,0.5)" if r == 1 else
        "rgba(229,57,53,0.6)"
        for r in flow_df["risk_label_next"]
    ]

    # -----------------------------
    # Create Sankey
    # -----------------------------
    fig = go.Figure(go.Sankey(
        arrangement="snap",
        node=dict(
            pad=25,
            thickness=30,
            label=labels,
            color=node_colors,
            line=dict(color="black", width=0.5)
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=link_colors
        )
    ))

    fig.update_layout(
        title=dict(
            text="AEWS – Identity Lifecycle → Next-Month Stress Flow",
            x=0.5,
            font=dict(size=20)
        ),
        font=dict(size=13),
        height=650
    )

    return fig
