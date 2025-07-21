import pandas as pd
import re
from thefuzz import fuzz, process

outcome_tracker_df = pd.read_csv("Outcome Tracker Undupes with System ID_2022_2025(OT Data).csv")
salesforce_df = pd.read_csv("Cook Source from SF with 18digit ID_061825(Salesforce Data).csv")

# Helper function to clean name
def clean_name(name):
    if pd.isna(name):
        return ""
    return re.sub(r"[^a-zA-Z\s]", "", str(name)).lower().strip()

# Cleaning name and email data
salesforce_df = salesforce_df.drop_duplicates(subset=["Applicant Contact: 18-Digit Account ID"]).copy()
salesforce_df["Cleaned Name"] = salesforce_df["Last Name"].apply(clean_name) + " " + salesforce_df["First Name"].apply(clean_name)
salesforce_df["Cleaned Email"] = salesforce_df["Applicant Contact: Email"].str.lower().str.strip()
outcome_tracker_df["Cleaned Email"] = outcome_tracker_df["Email Address"].str.lower().str.strip()

# Search through names
print("Searching through names...")

# Helper for name fuzzy matching
def find_best_match(ot_full_name, sf_names_check):
    ot_cleaned_name = clean_name(ot_full_name)
    if not ot_cleaned_name:
        return None, 0
    match, score = process.extractOne(ot_cleaned_name, sf_names_check, scorer = fuzz.token_sort_ratio)
    if score >= 95:
        return match, score
    else:
        return None, 0

# Matches every name in Outcome Tracker with the list of names in Salesforce.
sf_names_list = salesforce_df["Cleaned Name"].dropna().unique()
outcome_tracker_df[["Matched Name (Fuzzy)", "Match Score"]] = outcome_tracker_df.apply(
    lambda row: find_best_match(row["Full Name Last First Mdl"], sf_names_list), axis = 1, result_type = "expand"
)

# Search through emails
print("Searching through emails...")

# Matching email to names
empty_emails = ["xxxx@yahoo.com", "xxxx@gmail.com"]
sf_email_available = salesforce_df[~salesforce_df["Cleaned Email"].isin(empty_emails)]
sf_email_available = sf_email_available[sf_email_available["Cleaned Email"] != ""]
sf_email_to_name = sf_email_available.drop_duplicates(subset=["Cleaned Email"]).set_index("Cleaned Email")["Cleaned Name"]
outcome_tracker_df["Matched Name (Email)"] = outcome_tracker_df["Cleaned Email"].map(sf_email_to_name)

# Combines the email and fuzzy matches.
outcome_tracker_df["Matched Name"] = outcome_tracker_df["Matched Name (Email)"].fillna(outcome_tracker_df["Matched Name (Fuzzy)"])

# Export
print("Exporting...")

# Removes columns where theres no matched names and creates two maps.
matched_df = outcome_tracker_df.dropna(subset = ["Matched Name"]).copy()
sf_name_to_id = salesforce_df.drop_duplicates(subset=["Cleaned Name"]).set_index("Cleaned Name")["Applicant Contact: 18-Digit Account ID"]
sf_name_to_email = salesforce_df.drop_duplicates(subset=["Cleaned Name"]).set_index("Cleaned Name")["Cleaned Email"]

# Mapping cleaned names to their respective email and Salesforce ID.
matched_df['SF ID'] = matched_df['Matched Name'].map(sf_name_to_id)
matched_df['SF Contact Email'] = matched_df['Matched Name'].map(sf_name_to_email)

# Export the file.
matched_df.to_csv("Matched Data.csv", index = False)
print("Exported! Yay!")

