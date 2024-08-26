import os

import pandas as pd
import requests


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
    

def see_company_tickers():
    """
    look at the company_tickers json https://www.sec.gov/files/company_tickers.json
    {"0":{"cik_str":320193,"ticker":"AAPL","title":"Apple Inc."}, ...}
    """
    tickers_json = request_api("https://www.sec.gov/files/company_tickers.json")
    ticker_obj_list = list(tickers_json.values())[:10]
    for i in ticker_obj_list:
        print(i)


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


# Now that we have the cik we can look at 4 different URL API's:
# option #1 -> data.sec.gov/submissions/
def fetch_company_submission(cik_str: str) -> pd.DataFrame:
    """
    This JSON data structure contains metadata such as current name, former name, and stock exchanges and ticker symbols of publicly-traded companies.
    If the entity has additional filings, files will contain an array of additional JSON files and the date range for the filings each one contains.
    """
    submission_json = request_api(f"https://data.sec.gov/submissions/CIK{cik_str}.json")
    normalized_df = pd.json_normalize(
        submission_json
    )  # use json_normalize for semi-structured data
    return normalized_df


# option #2 -> data.sec.gov/api/xbrl/companyconcept/
def fetch_company_concept(cik_str: str) -> pd.DataFrame:
    """
    The company-concept API returns all the XBRL disclosures from a single company (CIK) and concept (a taxonomy and tag) into a single JSON file.
    """
    concept_json = request_api(
        f"https://data.sec.gov/api/xbrl/companyconcept/CIK{cik_str}/us-gaap/AccountsPayableCurrent.json"
    )
    normalized_df = pd.json_normalize(concept_json)
    return normalized_df


# option #3 -> data.sec.gov/api/xbrl/companyfacts/
def fetch_company_facts(cik_str: str) -> pd.DataFrame:
    """
    This API returns all the company concepts data for a company into a single API call:
    """
    facts_json = request_api(
        f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik_str}.json"
    )
    normalized_df = pd.json_normalize(facts_json)
    return normalized_df


# option#4 -> data.sec.gov/api/xbrl/frames/
def fetch_company_frames() -> pd.DataFrame:
    """
    The xbrl/frames API aggregates one fact for each reporting entity that is last filed that most closely fits the calendrical period requested.
    This API supports for annual and quarterly data.
    """
    frames_json = request_api(
        "https://data.sec.gov/api/xbrl/frames/us-gaap/Assets/USD/CY2019Q1I.json"
    )
    normalized_df = pd.json_normalize(frames_json)
    return normalized_df


def print_sec_results(ticker: str):
    """Show output of all 4 url's"""
    cik = fetch_cik(ticker)
    print(f"Company Submission df:{fetch_company_submission(cik).T}\n\n")
    print(f"Company Concept df:{fetch_company_concept(cik).T}\n\n")
    print(f"Company Facts df:{fetch_company_facts(cik).T}\n\n")
    print(f"Company Frames df:{fetch_company_frames().T}\n\n")


# We will focus our time on 'data.sec.gov/api/xbrl/companyfacts/' as that is where the most useful data is.
# Next we will clean our output from fetch_company_facts()


# MAYBE FIX
def show_company_facts_df(ticker_str: str, account: str) -> pd.DataFrame:
    """show company facts for specified account (i.e. 'Assets')"""
    cik_str = fetch_cik(ticker_str)
    facts_json = request_api(
        f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik_str}.json"
    )
    account_data = facts_json["facts"]["us-gaap"][account]["units"]["USD"]
    df = pd.DataFrame.from_dict(account_data)
    return df


# FIX ME
def clean_company_data(
    company_account_data_df: pd.DataFrame, account_name: str
) -> pd.DataFrame:
    """
    clean company JSON data and return a list of DataFrames
    :param json_file: dict: financial data for company
    :param account_list: list of account that user would like to add to df e.g 'Assets', 'Liabilities', etc.
    :return: list: list of dataframes for unique accounts
    """
    df = company_account_data_df
    df = df[
        df["fp"] == "FY"
    ]  # choose rows where fp == "FY" instead of 'form' beacuse of ifrs 20-F (== 10-K)
    df["year"] = pd.to_datetime(
        df["end"]
    ).dt.year  # convert "year" column into datetime object
    df = df.drop_duplicates(subset=["year"], keep="last")
    df = df[["year", "val"]]
    df = df.rename(columns={"val": account_name})
    return df


def merge_dfs(df_list: list[pd.DataFrame]) -> pd.DataFrame:
    cleaned_df_list = [df for df in df_list if not df.empty]

    merged_df = cleaned_df_list[0]
    for cdf in cleaned_df_list[1:]:
        merged_df = pd.merge(merged_df, cdf, on="year", how="outer")

    return merged_df


def add_extra_columns(cleaned_df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds 'valuation', 'ac/l', and 'cf/l' columns to the DataFrame where:
    - EARNINGS_MULTIPLIER is an arbitray multiple used to estimate company value based on future earnings.
    - 'valuation': (YEARS_TO_RECOVER_RETURN * CashFlows) + Cash - LongTermDebt
    - 'ac/l': Ratio of AssetsCurrent to Liabilities.
    - 'cf/l': Ratio of CashFlows to Liabilities.
    """
    # Add 'valuation' column
    EARNINGS_MULTIPLIER = 20
    cleaned_df["valuation"] = EARNINGS_MULTIPLIER * cleaned_df["NetIncome"]

    # Add 'NetInc./A' column
    cleaned_df["NetInc./A"] = round(cleaned_df["NetIncome"] / cleaned_df["Assets"], 2)

    return cleaned_df


def format_values(num: int) -> str:
    """
    To make data more readable

    Examples:
    >>> format_values(1_230_000_000_000)
    '1.23T'
    >>> format_values(4_560_000_000)
    '4.56B'
    >>> format_values(7_890_000)
    '7.89M'
    >>> format_values(123)
    '123'
    >>> format_values(-7_890_000_000)
    '-7.89B'
    """
    format_tuples = [(1e12, " T"), (1e9, " B"), (1e6, " M")]
    for threshold, suffix in format_tuples:
        if abs(num) >= threshold:
            return f"{num / threshold:.2f}{suffix}"
    return str(num)


def _format_values(merged_df: pd.DataFrame) -> pd.DataFrame:
    return merged_df.map(format_values)


pd.set_option("display.max_rows", 500)
pd.options.mode.chained_assignment = None

"""
TICKER = "META"
df1 = clean_company_data(show_company_facts_df(TICKER, "Assets"), "Assets")
df2 = clean_company_data(show_company_facts_df(TICKER, "NetIncomeLoss"), "NetIncome")
df_list = [df1, df2]
merged_df = merge_dfs(df_list)
result = add_extra_columns(merged_df)
print(result)
print()
print()
print(_format_values(result))
"""

TICKER = "META"
cik = fetch_cik(TICKER)
result = fetch_company_concept(cik)
print(result.T)
