# dashboard/state_cleaning.py

def clean_state_names(df):
    """
    Cleans and standardizes state names across datasets
    """

    df = df.copy()

    # Convert to string
    df["state"] = df["state"].astype(str)

    # Remove numeric / invalid states (e.g. 100000)
    df = df[~df["state"].str.isnumeric()]

    # Normalize text
    df["state"] = (
        df["state"]
        .str.strip()
        .str.title()
    )

    # Manual standardization mapping
    state_map = {
        "Andhrapradesh": "Andhra Pradesh",
        "Andhra Pradesh": "Andhra Pradesh",
        "Telengana": "Telangana",
        "Odisa": "Odisha",
        "Nct Of Delhi": "Delhi",
        "Delhi Nct": "Delhi",
        "Jammu & Kashmir": "Jammu And Kashmir"
    }

    df["state"] = df["state"].replace(state_map)

    return df
