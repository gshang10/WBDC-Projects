import pandas as pd
import re
from thefuzz import process, fuzz

# Loading the data.
outcome_tracker_df = pd.read_csv("Outcome Tracker Undupes with System ID_2022_2025(OT Data).csv")
salesforce_df = pd.read_csv("Cook Source from SF with 18digit ID_061825(Salesforce Data).csv")

# Helper function to clean names: lowercase, remove non-letters, and trim whitespace
def clean_name(name):
    # Safety check because some people did not fill out their names.
    if pd.isna(name):
        return ""
    # Removes everything but letters and spaces.
    name = re.sub(r"[^a-zA-Z\s]", "", str(name))
    return name.lower().strip()

# Using clean_name to name cleaned_sf_name column and make a unique list with it
salesforce_df["Cleaned_SF_Name"] =  salesforce_df["Last Name"].apply(clean_name) + " " + salesforce_df["First Name"].apply(clean_name)
sf_name_list = salesforce_df["Cleaned_SF_Name"].dropna().unique()

print("Finding the name matches...")

# Helper to find the best match for each person in OT
def find_best_match(ot_full_name, sf_names_to_check):
    cleaned_ot = clean_name(ot_full_name)
    # Again, safety check just in case nothing is filled.
    if not cleaned_ot:
        return None, 0
    # Extracts the highest matching score and returns the match 
    # if its greater than 85.
    best_match, score = process.extractOne(cleaned_ot, sf_names_to_check, scorer=fuzz.token_set_ratio)
    if score >= 90:
        return best_match, score
    else:
        return None, 0

# This iterates through each individual row of name in OT file, and compare the
#  name using the previous helper function and expand the 
outcome_tracker_df[["Matched_SF_Clean_Name", "Match_Score"]] = outcome_tracker_df.apply(
    lambda row: find_best_match(row['Full Name Last First Mdl'], sf_name_list), axis = 1, result_type = "expand"
)

# Drops duplicates from SF data based on their cleaned names.
sf_unique_names = salesforce_df.drop_duplicates(subset=["Cleaned_SF_Name"])

# Have a dictionary df by setting names as keys and account ID as value.
sf_name_to_id_map = sf_unique_names.set_index("Cleaned_SF_Name")["Applicant Contact: 18-Digit Account ID"]

# Map each name to their repsective id and creates a new column of SF ID.
outcome_tracker_df["Matched_SF_ID"] = outcome_tracker_df["Matched_SF_Clean_Name"].map(sf_name_to_id_map)

print("Now matching with emails...")

outcome_tracker_df['Cleaned_OT_Email'] = outcome_tracker_df['Email Address'].str.lower().str.strip()
salesforce_df['Cleaned_SF_Email'] = salesforce_df['Applicant Contact: Email'].str.lower().str.strip()

sf_unique_emails = salesforce_df.dropna(subset=['Cleaned_SF_Email']).drop_duplicates(subset=["Cleaned_SF_Email"])
sf_email_to_id_map = sf_unique_emails.set_index("Cleaned_SF_Email")["Applicant Contact: 18-Digit Account ID"]

email_matched_ids = outcome_tracker_df['Cleaned_OT_Email'].map(sf_email_to_id_map)
outcome_tracker_df['Matched_SF_ID'] = outcome_tracker_df['Matched_SF_ID'].fillna(email_matched_ids)

# Remove rows where there isn't a SF ID added and export.
export = outcome_tracker_df.dropna(subset = ["Matched_SF_ID"]).copy()
export.to_csv("test_file_2", index = False)
print("Export ready!")


