import pandas as pd

"""
WBDC keeps survery answers on a form on Outcome Tracker. 

I was given the task of taking the field in which clients filled 
out their source of funding for their business, and sorting each 
individual clients by their source of funding.

The difficulty is that each client fills out their form differently 
and we want other source of funding before funding from family and 
friends, so my solution was to use a keyword sorting loop as the 
entries of data are only in the hundreds.
"""

# Reads the file and drops unnecessary informations.
df = pd.read_csv("10. Economic Impact.csv")
df = df[df.columns[3:8]]

# Turns both funding details and capital infusions intwo lower case.
df["Funding Details"] = df["Funding Details"].str.lower().fillna("")

# Funders and its keywords that clients will fill out in Funding Details:
funders = {"Huntington Bank": ["huntington"],
           "BMO Harris Bank": ["bmo"],
            "Wintrust": ["wintrust"],
            "CIBC": ["cibc"],
            "SH Grant": ["sh grant", "sh scholarship"],
            "PPP/EIDL": ["ppp", "eidl"],
            "Strength and Grow Grant": ["strength and grow"],
            "CIBC": ["cibc"],
            "Polsky Grant" : ["polsky"],
            "US Bank": ["us bank", "u.s. bank"],
            "Capstone Partners" : ["capstone partners"],
            "Chase Bank": ["chase", "jp morgan", "jpmorgan"],
            "PNC Bank": ["pnc"],
            "Fifth Third Bank": ["fifth third", "5/3 bank", "5 3 bank"],
            "Bank of America": ["bank of america", "bofa"],
            "Wells Fargo": ["wells fargo"],
            "KeyBank": ["keybank", "key bank"],
            "Byline Bank" : [ "byline"],
            "A4CB": ["a4cb", "allies"],
            "Kiva": ["kiva"],
            "Accion": ["accion"],
            "Lendistry": ["lendistry"],
            "Bluevine": ["bluevine"],
            "Fundbox": ["fundbox"],
            "OnDeck": ["ondeck", "on deck"],
            "PayPal Capital": ["paypal"],
            "Square Capital": ["square"],
            "American Express": ["american express", "amex"],
            "Discover": ["discover"],
            "Capital One": ["capital one", "cap one"],
            "Credit Card": ["credit card"],
            "Angel Investor": ["angel investor", "angel funding"],
            "Private Investor": ["private investor", "private investment"],
            "Crowdfunding": ["crowdfund", "crowdfunding", "kickstarter", "indiegogo", "go fund me", "gofundme"],
            "Owner": ["owner", "family", "friend", "husband", "wife", "self", "personal"]}

# Loops through each row and only check ones where Funder Name haven't 
# been filled out yet.
for index, row in df.iterrows():
    if pd.isna(row["Funder Name(s)"]):

        # Loops over funders and its keywords that clients would use
        for funder, keywords in funders.items():
            for keyword in keywords:

                # If keyword is in Funding Detail, add it to the Funder Name.
                if keyword in row["Funding Details"]:
                    current = df.at[index, "Funder Name(s)"]
                    if pd.isna(current):
                        df.at[index, "Funder Name(s)"] = funder

                    # If Funder Name already have other funders that's been 
                    # filled by the loop, join with a comma.
                    else:
                        if funder not in df.at[index, "Funder Name(s)"]:
                            df.at[index, "Funder Name(s)"] = current  + ", " + funder

df = df.sort_values(by="Funder Name(s)")

print(df)
df.to_csv("funder-filled.csv", index = False)