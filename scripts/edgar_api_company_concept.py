import os

import matplotlib.pyplot as plt
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()


def load_env_var(var_name: str) -> str:
    """Function to load an environment variable"""
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


# first step is to get CIK of the stock you want info for
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


def get_company_concept_account(company_name: str, account: str) -> pd.DataFrame:
    """
    The company-concept API returns all the XBRL disclosures from a single company (CIK) and concept (a taxonomy and tag) into a single JSON file.
    """
    cik_str = fetch_cik(company_name)
    concept_json = request_api(
        f"https://data.sec.gov/api/xbrl/companyconcept/CIK{cik_str}/us-gaap/{account}.json"
    )
    account_json_data = concept_json["units"]["USD"]
    normalized_df = pd.json_normalize(account_json_data)
    clean_df = normalized_df[normalized_df["fp"] == "FY"]
    # change 'year' column to datetime type before dropping
    clean_df["year"] = pd.to_datetime(clean_df["end"]).dt.year
    clean_df = clean_df.drop_duplicates(subset=["year"], keep="last")
    clean_df = clean_df[["year", "val"]]
    clean_df = clean_df.rename(columns={"val": company_name, "year": account})

    return clean_df


def compare_companies(
    companies_list: list[str], account: str, account_rename: str
) -> pd.DataFrame:
    final_df = get_company_concept_account(companies_list[0], account)
    for company in companies_list[1:]:
        current_df = get_company_concept_account(company, account)
        final_df = pd.merge(final_df, current_df, on=account, how="outer")

    final_df = final_df.rename(columns={account: account_rename})
    return final_df


def format_values(num: int) -> str:
    """
    To make data more readable
    Example:
    format_values(1_230_000_000_000)
    '1.23 T'
    """
    format_tuples = [(1e12, " T"), (1e9, " B"), (1e6, " M"), (1e6, " K")]
    for threshold, suffix in format_tuples:
        if abs(num) >= threshold:
            return f"{num / threshold:.2f}{suffix}"
    return str(num)


def _format_values(int_df: pd.DataFrame) -> pd.DataFrame:
    """helper function for format_values()"""
    return int_df.map(format_values)


def plot_df(dataframe: pd.DataFrame, account: str):
    """plot a line chart for a pandas df"""
    # Set the 'Year' column as the index
    df = result.set_index(account)
    df.plot(kind="line")

    plt.show()


companies_to_compare_list = ["META", "AAPL", "AMZN", "GOOG"]
result = compare_companies(
    companies_to_compare_list, "NetCashProvidedByUsedInOperatingActivities", "cashFlows"
)

result["cashFlows"] = result["cashFlows"].astype(int)
result = result[result["cashFlows"] > 2015]

with pd.option_context("display.max_columns", 10):
    print(result)
    print(_format_values(result))

# plot_df(result, "cashFlows")
