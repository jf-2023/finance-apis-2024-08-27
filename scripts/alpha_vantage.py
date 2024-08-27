import os

import pandas as pd
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


TICKER = "META"
api_key = load_env_var("ALPHA_VANTAGE_API_KEY")

url = f"https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol={TICKER}&apikey={api_key}"
r = requests.get(url)
result = r.json()
print(pd.json_normalize(result).T)
data = result["annualReports"]
print(pd.DataFrame(data).T)
