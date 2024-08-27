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


def get_market_cap(ticker_str: str) -> int:
    """
    get the market capitalization of specified stock ticker, returns int or float
    """
    apikey = load_env_var("AV_API_KEY")
    url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker_str}&apikey={apikey}"
    r = requests.get(url)
    r_json = r.json()
    latest_price = r_json["MarketCapitalization"]
    latest_price = int(latest_price)
    return latest_price


def get_valuation_from_db(ticker_str: str) -> int:
    """connect to mongodb to get calculated valuation"""
    try:
        client = pymongo.MongoClient()

        db = client["hacker"]
        dojo_collection = db["dojo"]

        retrieved_document = dojo_collection.find_one({"ticker": ticker_str})
        calculated_valuation = int(retrieved_document["valuation"])

        client.close()

        return calculated_valuation

    except TypeError as e:
        raise TypeError(f"Document not found: {e}")


def check_buying_opportunity(ticker_str: str):
    """ check calculated valuation with current price and check for possible buying opportunity"""
    valuation = get_valuation_from_db(ticker_str)
    current_price = get_market_cap(ticker_str)
    if current_price <= valuation:
        print(f"{ticker_str} might be a buying opportunity, DO MORE RESEARCH FIRST!")
    else:
        print(
            f"{ticker_str} might be overpriced, PROCEED WITH CAUTION AND DO MORE RESEARCH!"
        )


TICKER = "MU"
check_buying_opportunity(TICKER)
