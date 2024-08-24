import pymongo
import requests

TICKER = "IBM"
url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={TICKER}&interval=5min&apikey=demo"
r = requests.get(url)
r_json = r.json()
latest_price = r_json["Meta Data"]['3. Last Refreshed']
latest_price = r_json["Time Series (5min)"][latest_price]['4. close']
latest_price = eval(latest_price)

client = pymongo.MongoClient()

db = client["hacker"]
dojo_collection = db["dojo"]


retrieved_document = dojo_collection.find_one({"name": "QUACK"})
valuation = retrieved_document["valuation"]
entity_name = retrieved_document["name"]

client.close()

if latest_price <= valuation:
    print(f"{entity_name} might be a buying opportunity, DO MORE RESEARCH FIRST!")
else:
    print(f"{entity_name} might be overpriced, PROCEED WITH CAUTION AND DO MORE RESEARCH!")