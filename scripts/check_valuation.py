import os

import pymongo
import requests
from dotenv import load_dotenv


def load_env_var(var_name: str) -> str:
    """Function to load an environment variable"""
    load_dotenv()
    value = os.getenv(var_name)
    if value is None:
        raise ValueError(
            f"Environment variable '{var_name}' not found.\n"
            f"Please make sure you made a .env file with your email address"
        )
    return value


TICKER = "MU"
apikey = load_env_var("AV_API_KEY")
url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={TICKER}&apikey={apikey}"
r = requests.get(url)
r_json = r.json()
latest_price = r_json["MarketCapitalization"]
latest_price = eval(latest_price)
print(latest_price)

client = pymongo.MongoClient()

db = client["hacker"]
dojo_collection = db["dojo"]


retrieved_document = dojo_collection.find_one({"ticker": TICKER})

valuation = retrieved_document["valuation"]

print(valuation)
entity_name = retrieved_document["ticker"]

client.close()

if latest_price <= valuation:
    print(f"{entity_name} might be a buying opportunity, DO MORE RESEARCH FIRST!")
else:
    print(
        f"{entity_name} might be overpriced, PROCEED WITH CAUTION AND DO MORE RESEARCH!"
    )
