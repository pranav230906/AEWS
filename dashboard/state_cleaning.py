# dashboard/state_cleaning.py

import re

# ================================================================
# CANONICAL STATE NAMES
# Single source of truth for all Indian state / UT names
# ================================================================
CANONICAL_STATE_MAP = {
    # ── Andaman & Nicobar Islands ────────────────────────────────
    "Andaman And Nicobar Islands":                  "Andaman & Nicobar Islands",
    "Andaman & Nicobar Islands":                    "Andaman & Nicobar Islands",

    # ── Andhra Pradesh ───────────────────────────────────────────
    "Andhrapradesh":                                "Andhra Pradesh",
    "Andhra Pradesh":                               "Andhra Pradesh",

    # ── Dadra & Nagar Haveli ─────────────────────────────────────
    "Dadra And Nagar Haveli":                       "Dadra & Nagar Haveli",
    "Dadra & Nagar Haveli":                         "Dadra & Nagar Haveli",
    "Dadra And Nagar Haveli And Daman And Diu":     "Dadra & Nagar Haveli and Daman & Diu",
    "The Dadra And Nagar Haveli And Daman And Diu": "Dadra & Nagar Haveli and Daman & Diu",

    # ── Daman & Diu ──────────────────────────────────────────────
    "Daman And Diu":                                "Daman & Diu",
    "Daman & Diu":                                  "Daman & Diu",

    # ── Delhi ────────────────────────────────────────────────────
    "Nct Of Delhi":                                 "Delhi",
    "Delhi Nct":                                    "Delhi",
    "Delhi":                                        "Delhi",

    # ── Jammu & Kashmir ──────────────────────────────────────────
    "Jammu And Kashmir":                            "Jammu & Kashmir",
    "Jammu & Kashmir":                              "Jammu & Kashmir",

    # ── Odisha ───────────────────────────────────────────────────
    "Odisa":                                        "Odisha",
    "Orissa":                                       "Odisha",
    "Odisha":                                       "Odisha",

    # ── Puducherry ───────────────────────────────────────────────
    "Pondicherry":                                  "Puducherry",
    "Puducherry":                                   "Puducherry",

    # ── Telangana ────────────────────────────────────────────────
    "Telengana":                                    "Telangana",
    "Telangana":                                    "Telangana",

    # ── West Bengal ──────────────────────────────────────────────
    "Westbengal":                                   "West Bengal",
    "West Bangal":                                  "West Bengal",
    "West  Bengal":                                 "West Bengal",
    "West Bengal":                                  "West Bengal",
}


# ================================================================
# CANONICAL DISTRICT NAMES
# Single source of truth for all district name variants
# ================================================================
CANONICAL_DISTRICT_MAP = {
    # ── Compound names written as one word ──────────────────────
    "Ahmed Nagar":          "Ahmednagar",
    "Ashok Nagar":          "Ashoknagar",
    "Banas Kantha":         "Banaskantha",
    "Bara Banki":           "Barabanki",
    "Cooch Behar":          "Coochbehar",
    "Karim Nagar":          "Karimnagar",
    "Kushi Nagar":          "Kushinagar",
    "Mahabub Nagar":        "Mahabubnagar",
    "Panch Mahals":         "Panchmahals",
    "Rae Bareli":           "Raebareli",
    "Ranga Reddy":          "Rangareddy",
    "Sabar Kantha":         "Sabarkantha",
    "Siddharth Nagar":      "Siddharthnagar",
    "Surendra Nagar":       "Surendranagar",
    "Yamuna Nagar":         "Yamunanagar",

    # ── Hyphenated / separator variants ─────────────────────────
    "Janjgir - Champa":     "Janjgir-Champa",
    "Janjgir Champa":       "Janjgir-Champa",
    "Medchal Malkajgiri":   "Medchal-Malkajgiri",
    "Medchal?Malkajgiri":   "Medchal-Malkajgiri",   # garbled char
    "Medchal\u2212Malkajgiri": "Medchal-Malkajgiri",  # unicode minus

    # ── Trailing asterisks (data annotation artefacts) ──────────
    "Bagalkot *":           "Bagalkot",
    "Bokaro *":             "Bokaro",
    "Chamarajanagar *":     "Chamarajanagar",
    "Dhalai *":             "Dhalai",
    "Dhalai  *":            "Dhalai",
    "Gadag *":              "Gadag",
    "Garhwa *":             "Garhwa",
    "Gondiya *":            "Gondiya",
    "Harda *":              "Harda",
    "Haveri *":             "Haveri",
    "Hingoli *":            "Hingoli",
    "Jhajjar *":            "Jhajjar",
    "Kendrapara *":         "Kendrapara",
    "Kushinagar *":         "Kushinagar",
    "Namakkal *":           "Namakkal",
    "Namakkal   *":         "Namakkal",
    "Nandurbar *":          "Nandurbar",
    "North East *":         "North East",
    "North East   *":       "North East",
    "Udupi *":              "Udupi",
    "Washim *":             "Washim",

    # ── Parenthetical / disambiguation suffixes ──────────────────
    "Aurangabad(Bh)":           "Aurangabad",
    "Bijapur(Kar)":             "Bijapur",
    "Kaimur (Bhabua)":          "Kaimur",
    "Leh (Ladakh)":             "Leh",
    "Mumbai( Sub Urban )":      "Mumbai Suburban",
    "Raigarh(Mh)":              "Raigarh",
    "S.A.S Nagar(Mohali)":      "Sahibzada Ajit Singh Nagar",
    "Sas Nagar (Mohali)":       "Sahibzada Ajit Singh Nagar",
    "Warangal (Urban)":         "Warangal Urban",

    # ── K.V. Rangareddy ──────────────────────────────────────────
    "K.V.Rangareddy":           "K.V. Rangareddy",

    # ── Spacing fixes (after title-casing) ───────────────────────
}


def _normalize(name: str) -> str:
    """
    Light normalization before dictionary lookup:
      - strip whitespace
      - collapse multiple spaces into one
      - title-case
    """
    name = name.strip()
    name = re.sub(r"\s+", " ", name)
    name = name.title()
    return name


def clean_state_names(df):
    """
    Cleans and standardizes 'state' (and 'district' if present) columns
    across all datasets. This is the single source of truth for name
    normalization in the entire AEWS app.

    Steps:
      1. Drop rows where 'state' is purely numeric (junk rows like 100000).
      2. Normalize whitespace + title-case for both columns.
      3. Apply canonical mappings so every variant resolves to one name.
    """
    df = df.copy()

    # ── STATE column ─────────────────────────────────────────────
    if "state" in df.columns:
        df["state"] = df["state"].astype(str)

        # Drop numeric / invalid state rows
        df = df[~df["state"].str.strip().str.isnumeric()]

        # Normalize whitespace & casing
        df["state"] = df["state"].apply(_normalize)

        # Map to canonical state names
        df["state"] = df["state"].replace(CANONICAL_STATE_MAP)

    # ── DISTRICT column ──────────────────────────────────────────
    if "district" in df.columns:
        df["district"] = df["district"].astype(str)

        # Normalize whitespace & casing
        df["district"] = df["district"].apply(_normalize)

        # Map to canonical district names (post-normalize keys)
        df["district"] = df["district"].replace(CANONICAL_DISTRICT_MAP)

    return df
