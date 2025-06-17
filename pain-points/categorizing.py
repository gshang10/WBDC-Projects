import pandas as pd

# Reads the file and combines magic wand question with challenges 
# question into a new column named 'words'.
df = pd.read_excel('data.xlsx')
df['words'] = df['wand'].fillna('') + ' ' + df['challenges'].fillna('')

# Removes old columns, cleans the 'words' column.
df = df.drop('wand', axis = 1)
df = df.drop('challenges', axis = 1)
df['words'] = df['words'].str.lower()
df['words'] = df['words'].str.replace('[^a-z\s]', '', regex=True)

# Keyword for each category.
keywords = {
    'capital': ["funding", "capital", "grant", "loan", "crowdfunding", 
                "investor", "finance", "financial", "money", "cost"],
    'marketing': ["marketing", "sales", "client", "customer", "website", 
                  "online", "shopify", "brand", "social media", "seo", 
                  "grow", "growth", "promotion", "advertising"],
    'management': ["price", "cash", "cashflow", "bookkeeping", "strategy", 
                   "staff", "employee", "operations", "process", "pitch", 
                   "organization", "management", "inventory", "budget"],
    'planning': ["start", "starting", "launch", "begin", "business plan", 
                 "roadmap", "idea", "plan", "validation", "step", "how to"],
    'legal': ["llc", "trademark", "license", "licensing", "certification", 
              "fda", "minority", "disability", "legal", "patent", 
              "compliance", "permit", "incorporate"],
    'network': ["network", "connection", "partner", "partnership", 
                "referral", "mentor", "events", "community", 
                "relationship", "outreach", "introduce"]}

# Initializes category to 0
for category in keywords:
    df[category] = 0

# Iterates over each row, iterates each category and its list of keywords.
for index, row in df.iterrows():
    for category, list in keywords.items():
        # For each keyword in the list, if the keyword is in 'words', 
        # update the corresponding category at that row to 0.
        for keyword in list:
            if keyword in row['words']:
                df.at[index, category] = 1


print(df.head(5))
df.to_csv('filtered-data.csv')