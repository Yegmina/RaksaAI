import pandas as pd

with open("filtered_list_of_industries.txt", "r", encoding="utf-8") as file: #filter for wanted industries
    filter_list = [line.strip() for line in file]

df = pd.read_csv("filtered_active_companies_cleaned.csv")

filtered_df = df[df["mainBusinessLine.descriptions"].isin(filter_list)]

filtered_df.to_csv("relevant_companies_last_search.csv", index=False)
