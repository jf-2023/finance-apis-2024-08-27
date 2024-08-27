import os

import matplotlib.pyplot as plt
import pandas as pd
import pymongo
import requests
from dotenv import load_dotenv


def format_values(num: int) -> str:
    """
    To make data more readable
    Example:
    format_values(1_230_000_000_000)
    '1.23T'
    """
    format_tuples = [(1e12, " T"), (1e9, " B"), (1e6, " M"), (1e6, " K")]
    for threshold, suffix in format_tuples:
        if abs(num) >= threshold:
            return f"{num / threshold:.2f}{suffix}"
    return str(num)


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


def fetch_cik(company_name: str = "") -> str:
    """
    GET CIK id for the specified company name. If no company name is passed,
    the function will return a CIK id for a random company.

    :param company_name: str, user-specified company ticker symbol, e.g., 'AMZN' for Amazon.
    :return: str, CIK id of the specified or random company. Must be a width of 10 characters.
    """
    tickers_json = request_api("https://www.sec.gov/files/company_tickers.json")

    company_name = company_name.upper()
    if company_name:
        for obj in tickers_json.values():
            if obj["ticker"] == company_name:
                return f'{obj["cik_str"]:010}'
    print(
        f"the cik for {company_name} was not found, giving cik for AAPL instead by default"
    )
    return f"{0:010}"


def fetch_cik_obj(company_name: str = "") -> dict:
    tickers_json = request_api("https://www.sec.gov/files/company_tickers.json")

    company_name = company_name.upper()
    for obj in tickers_json.values():
        if obj["ticker"] == company_name:
            return obj
    else:
        print(f"No object for {company_name} was found, returning empty dict")
        return {}


def show_company_facts_keys(cik_str: str) -> pd.DataFrame:
    """
    This API returns all the company concepts data for a company into a single API call:
    """
    facts_json = request_api(
        f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik_str}.json"
    )
    normalized_df = pd.json_normalize(facts_json)
    return normalized_df.T


def fetch_company_facts_data_list(
    company_name: str, account_list: list[str]
) -> list[pd.DataFrame]:
    """
    clean company JSON data and return a list of DataFrames
    :param company_name: name of stock ticker
    :param account_list: list of account that user would like to add to df e.g 'Assets', 'Liabilities', etc.
    :return: list: list of dataframes for unique accounts
    """
    cik_str = fetch_cik(company_name)
    facts_json = request_api(
        f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik_str}.json"
    )
    company_dfs = []
    for account in account_list:
        try:
            acc_data = facts_json["facts"]["us-gaap"][account]["units"]["USD"]
            df = pd.DataFrame.from_dict(acc_data)
            df = df[df["fp"] == "FY"]
            df["year"] = pd.to_datetime(df["end"]).dt.year
            df = df.drop_duplicates(subset=["year"], keep="last")
            df = df[["year", "val"]]
            df = df.rename(columns={"val": account})
            company_dfs.append(df)
        except KeyError as e:
            print(f"df could not be processed for: {e}")
            company_dfs.append(pd.DataFrame({}))
    return company_dfs


def merge_final_df(df_list: list[pd.DataFrame]) -> pd.DataFrame:
    """merge list of dfs and return df"""
    cleaned_df_list = [df for df in df_list if not df.empty]

    merged_df = cleaned_df_list[0]
    for cdf in cleaned_df_list[1:]:
        merged_df = pd.merge(merged_df, cdf, on="year", how="outer")

    return merged_df


def add_valuation(cleaned_df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds 'valuation' column to the DataFrame where:
    - EARNINGS_MULTIPLIER is an arbitrary multiple used to estimate company value based on future earnings.
    - 'valuation': (YEARS_TO_RECOVER_RETURN * CashFlows) + Cash - LongTermDebt
    """
    # Add 'valuation' column
    earnings_multiplier = 20
    cleaned_df["valuation"] = (
        (earnings_multiplier * cleaned_df["CashFlows"])
        + cleaned_df["Cash"]
        - cleaned_df["LongTermDebt"]
    )

    return cleaned_df


def process_financial_data(ticker: str = "META") -> pd.DataFrame:
    specified_accounts = [
        "NetCashProvidedByUsedInOperatingActivities",
        "CashAndCashEquivalentsAtCarryingValue",
        "Liabilities",
        "AssetsCurrent",
        "Revenues",
        "Assets",
        "NetIncomeLoss",
        "LongTermDebt",
    ]
    accounts_to_drop = ["AssetsCurrent"]
    accounts_to_rename = {
        "NetCashProvidedByUsedInOperatingActivities": "CashFlows",
        "CashAndCashEquivalentsAtCarryingValue": "Cash",
    }

    company_data = fetch_company_facts_data_list(ticker, specified_accounts)
    result_df = merge_final_df(company_data)
    result_df = result_df.rename(columns=accounts_to_rename)
    result_df = result_df.drop(columns=accounts_to_drop)

    return result_df


def show_matplot(company_ticker: str):
    data_df = process_financial_data(company_ticker)
    data_df = data_df.set_index("year")

    data_df.plot(kind="line")

    plt.title(f"Financials for: {company_ticker}")
    plt.xlabel("Year")
    plt.ylabel("amount")
    plt.grid(True)

    plt.show()


def get_formatted_financials(ticker: str):
    earnings_multiplier = 20
    average_years_timeframe = 3

    result_df = process_financial_data(ticker)
    result_df = add_valuation(result_df)
    result_df["year"] = result_df["year"].astype(str)
    result_df.set_index("year", inplace=True)
    current_value = result_df.tail(average_years_timeframe)["CashFlows"].mean()
    value_dict = {"valuation": int(current_value * earnings_multiplier)}
    financials_dict = result_df.to_dict()
    result_dict = fetch_cik_obj(ticker)
    result_dict.update(financials_dict)
    result_dict.update(value_dict)

    return result_dict


def upload_to_mongodb(ticker: str):
    client = pymongo.MongoClient()
    db = client["hacker"]
    collection = db["dojo"]

    formatted_financials = get_formatted_financials(ticker)
    print(formatted_financials)
    # Insert into MongoDB collection
    collection.insert_one(formatted_financials)
    print("Data inserted successfully into MongoDB.")

    client.close()


upload_to_mongodb("META")
