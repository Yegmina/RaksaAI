import pandas as pd
import json

with open("data_20241118.json", encoding="utf-8") as file: #downloaded this from Finnish patent and registration office.
    data = json.load(file)

df = pd.json_normalize(data)

df_active = df[df["status"] == "2"] #active orgs filter


df_filtered = df_active[["website.url", "mainBusinessLine.descriptions"]].copy()

def extract_english_description(descriptions):
    if isinstance(descriptions, list):
        for desc in descriptions:
            if desc.get("languageCode") == "3":
                return desc.get("description", None)
    return None

df_filtered["mainBusinessLine.descriptions"] = df_filtered["mainBusinessLine.descriptions"].apply(extract_english_description)

# Filter out rows with no websites or no English description
df_filtered = df_filtered[
    df_filtered["website.url"].notna() & (df_filtered["website.url"].str.strip() != "") & 
    df_filtered["mainBusinessLine.descriptions"].notna()
]
df_filtered = df_filtered.drop_duplicates(subset=["website.url", "mainBusinessLine.descriptions"])
# Save to CSV
df_filtered.to_csv("filtered_active_companies_cleaned.csv", index=False)