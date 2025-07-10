import pandas as pd
import re
from thefuzz import fuzz, process

outcome_tracker_df = pd.read_csv("Outcome Tracker Undupes with System ID_2022_2025(OT Data).csv")
salesforce_df = pd.read_csv("Cook Source from SF with 18digit ID_061825(Salesforce Data).csv")

# Helper function to clean name
def clean_name(name):
    if pd.isna(name):
        return ""
    return re.sub(r"[^a-zA-Z\s]", "", name).lower().strip()

# Cleaning name and email data
salesforce_df["Cleaned Name"] = salesforce_df["Last Name"].apply(clean_name) + " " + salesforce_df["First Name"].apply(clean_name)
salesforce_df["Cleaned Email"] = salesforce_df["Applicant Contact: Email"].str.lower().str.strip()
outcome_tracker_df["Cleaned Email"] = salesforce_df["Email Address"].lower().strip()

### SEARCHING EMAIL
print("Searching through emails...")

# Matching email to names
sf_emai_to_name = salesforce_df.drop_duplicates(subset=["Cleaned Email"]).set_index("Cleaned Email")["Cleaned Name"]
outcome_tracker_df["Matched Name"] = outcome_tracker_df["Cleaned Email"].map(sf_emai_to_name)


### SEARCHING NAMES
print("Searching through names...")

# Helper for name fuzzy matching
def find_best_match(ot_full_name, sf_names_check):
    ot_cleaned_name = clean_name(ot_full_name)
    if not ot_cleaned_name:
        return None, 0
    match, score = process.extractOne(ot_cleaned_name, sf_names_check, scorer = fuzz.token_set_ratio)
    if score >= 95:
        return match, score
    else:
        return None, 0

sf_names = salesforce_df["Cleaned Name"].dropna().unique()

outcome_tracker_df[["Matched Name", "Match Score"]] = outcome_tracker_df.apply(
    lambda row: find_best_match(row["Full Name Last First Mdl"], sf_names), axis = 1, result_type = "expand"
)

print(outcome_tracker_df.head(5))

