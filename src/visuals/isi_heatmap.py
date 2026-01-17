import seaborn as sns
import matplotlib.pyplot as plt

def plot_isi_heatmap(df, state_name):
    subset = df[df["state"] == state_name]

    pivot = subset.pivot(
        index="district",
        columns="year_month",
        values="isi_score"
    )

    plt.figure(figsize=(14, 8))
    sns.heatmap(pivot, cmap="Reds")
    plt.title(f"Identity Stress Index Heatmap – {state_name}")
    plt.show()
