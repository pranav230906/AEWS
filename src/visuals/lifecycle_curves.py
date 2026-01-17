import matplotlib.pyplot as plt

def plot_lifecycle_curves(age_df):
    plt.figure(figsize=(10, 6))

    plt.plot(age_df["age_group"], age_df["enrolment"], label="Enrolment")
    plt.plot(age_df["age_group"], age_df["demographic"], label="Demographic Updates")
    plt.plot(age_df["age_group"], age_df["biometric"], label="Biometric Updates")

    plt.xlabel("Age Group")
    plt.ylabel("Normalized Activity")
    plt.title("Identity Lifecycle Activity Curves")
    plt.legend()
    plt.show()
  