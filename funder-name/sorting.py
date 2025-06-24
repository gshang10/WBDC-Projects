import pandas as pd

# Reads the file and drops unnecessary informations.
df = pd.read_csv("10. Economic Impact.csv")
df = df[df.columns[4:8]]

# Turns both funding details and capital infusions intwo lower case.
df["Funding Details"] = df["Funding Details"].str.lower().fillna("")

# Funders and its keywords that clients will fill out in Funding Details:
funders = {
    "Huntington Bank" : ["huntington", "huntington bank"],
    "Kiva" : ["kiva"],
    "A4CB" : ["a4cb", "allies"], 
    "American Express" : ["american express"],
    "Wintrust" : ["wintrust"],
    "US Bank" : ["us bank"],
    "Chase Bank" : ["chase bank", "chase"],
    "BMO" : ["bmo"],
    "Owner": ["owner", "family", "friend", "husband", "wife", "self-funded", "self funded", "self"]}

# Loops through each row and only check ones where Funder Name haven't 
# been filled out yet.
for index, row in df.iterrows():
    if pd.isna(row["Funder Name(s)"]):

        # Loops over funders and its keywords that clients would use
        for funder, keywords in funders.items():
            for keyword in keywords:

                # If keyword is in Funding Detail, add it to the Funder Name.
                if keyword in row["Funding Details"]:
                    if pd.isna(row["Funder Name(s)"]):
                        df.at[index, "Funder Name(s)"] = funder

                    # If Funder Name already have other funders that's been 
                    # filled by the loop, join with a comma.
                    elif pd.notna(row["Funder Name(s)"]):
                        df.at[index, "Funder Name(s)"] = df.at[index, "Funder Name(s)"]  + ", " + funder


df = df.drop("Funding Details", axis = 1)
print(df)