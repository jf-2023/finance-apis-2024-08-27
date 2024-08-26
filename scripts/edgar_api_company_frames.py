import os

import pandas as pd
import requests
from dotenv import load_dotenv

# Load the .env file
load_dotenv()


def load_env_var(var_name: str) -> str:
    """Function to load an environment variable"""
    value = os.getenv(var_name)
    if value is None:
        raise ValueError(f"Environment variable '{var_name}' not found.")
    return value


def request_api(api_url: str) -> dict:
    """
    Sends a GET request to the specified API URL with a User-Agent header.

    Returns:
        Dict[str, Any]: The JSON response from the API as a dictionary.

    Raises:
        requests.RequestException: For issues with the request.
    """
    user_agent = load_env_var("EMAIL_ADDRESS")
    headers = {"User-Agent": user_agent}
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise RuntimeError(f"An error occurred while requesting the API: {e}")


def get_account_frames(account: str, period: str) -> pd.DataFrame:
    """
    The xbrl/frames API aggregates one fact for each reporting entity that is last filed that most closely fits the calendrical period requested.
    The period format is CY#### for annual data, CY####Q# for quarterly data, and CY####Q#I for instantaneous data.
    """
    frames_json = request_api(
        f"https://data.sec.gov/api/xbrl/frames/us-gaap/{account}/USD/{period}.json"
    )
    json_data = frames_json["data"]
    df = pd.json_normalize(json_data)
    df = df[["entityName", "val"]]
    df = df.rename(columns={"val": account})
    sorted_df = df.sort_values(by=account, ascending=False)
    return sorted_df


df1 = get_account_frames("OperatingIncomeLoss", "CY2022")
print(df1)
df2 = get_account_frames("Assets", "CY2022Q4I")
print(df2)

merged_df = pd.merge(df1, df2, on="entityName")
merged_df["OROA"] = round(merged_df["OperatingIncomeLoss"] / merged_df["Assets"], 2)
merged_df = merged_df.sort_values(by="OROA", ascending=False)
merged_df = merged_df.rename(columns={"OperatingIncomeLoss": "OperatingIncome"})
# merged_df = merged_df[merged_df["OROA"] < 0.50]
with pd.option_context("display.max_columns", 10):
    print(merged_df.head(20))
