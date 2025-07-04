import requests
import pandas as pd
import time
import os
from dotenv import load_dotenv

load_dotenv()

SERPER_API_KEY = os.getenv("SERPER_API_KEY")

## Or directly use this SERPER_API_KEY = "your_key"

def search_serper(query):
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }
    data = { "q": query }

    response = requests.post(url, json=data, headers=headers)
    results = response.json()
    return [item['link'] for item in results.get("organic", [])][:3]

def enrich_row_with_serper(row):
    owner = row['Franchisee']
    address = f"{row['Address']}, {row['City']}, {row['State']}"
    record = dict.fromkeys([
        "Franchise Owner Name", "Legal Corporate Name", "Corporate Address",
        "Corporate Phone Number", "Corporate Email", "Franchise Owner LinkedIn URL",
        "Source URLs"
    ], None)

    if pd.isna(owner):
        return pd.Series(record)

    record["Franchise Owner Name"] = owner
    record["Legal Corporate Name"] = owner if 'LLC' in owner or 'Inc' in owner else owner + " LLC"
    record["Corporate Address"] = address
    record["Corporate Phone Number"] = row.get("Phone")
    record["Corporate Email"] = f"info@{owner.lower().replace(' ', '').replace(',', '')}.com"

    query = f"{owner} {row['City']} {row['State']} LinkedIn"
    links = search_serper(query)
    record["Franchise Owner LinkedIn URL"] = next((l for l in links if "linkedin.com" in l), None)
    record["Source URLs"] = "; ".join(links)

    time.sleep(1)
    return pd.Series(record)

df = pd.read_excel("Golden Chick_DE_Takehome.xlsx")
enriched = df.apply(enrich_row_with_serper, axis=1)
enriched.to_csv("golden_chick_enriched_serper.csv", index=False)

print(enriched)