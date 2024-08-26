import pandas as pd
import requests

TICKER = "IBM"
url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={TICKER}&interval=5min&apikey=demo"
r = requests.get(url)
r_json = r.json()
latest_price = r_json["Meta Data"]["3. Last Refreshed"]
result = r_json["Time Series (5min)"][latest_price]["4. close"]
print(f"latest price for {TICKER} (5min interval): {result}")


url2 = "https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol=IBM&apikey=demo"
r2 = requests.get(url2)
result2 = r2.json()
print(pd.json_normalize(result2).T)
data = result2["annualReports"]
print(pd.DataFrame(data).T)
