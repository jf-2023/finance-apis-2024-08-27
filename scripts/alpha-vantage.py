import os

import pandas as pd
import requests


def load_env_var(var_name: str) -> str:
    """Function to load an environment variable"""
    value = os.getenv(var_name)
    if value is None:
        raise ValueError(f"Environment variable '{var_name}' not found.")
    return value


ticker = "MU"
api_key = load_env_var("ALPHA_VANTAGE_API_KEY")
"""
url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey={api_key}'
r = requests.get(url)
data = r.json()

days_data = list(data.values())[1]
current_day_data = list(days_data.values())[0]
closing_price = current_day_data["4. close"]
print(f"The closing price for {ticker} is: {closing_price}")
"""

url = f"https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={ticker}&apikey={api_key}"
r = requests.get(url)
data = r.json()
data_dict = data["annualReports"]
normalized_df = pd.json_normalize(data_dict)
normalized_df = normalized_df[["fiscalDateEnding", "totalRevenue"]]

print(normalized_df)
