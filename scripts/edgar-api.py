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
                print()
                print(obj)
                print(f"the cik for {company_name} is: {obj['cik_str']}")
                print()
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
        "https://data.sec.gov/api/xbrl/frames//ifrs-full/Assets/USD/CY2019Q1I.json"
    )
    normalized_df = pd.json_normalize(frames_json)
    return normalized_df


cik = fetch_cik("META")
# Show output of all 4 url's
print(fetch_company_submission(cik).T)
print(fetch_company_concept(cik).T)
print(fetch_company_facts(cik).T)
print(fetch_company_frames().T)


# We will focus our time on 'data.sec.gov/api/xbrl/companyfacts/' as that is where the most useful data is.
# Next we will clean our output from fetch_company_facts()
