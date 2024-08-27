# Finance API Presentation at Hacker Dojo on 08/27/24

This repository outlines the upcoming talk scheduled for 08/27/24 at Hacker Dojo. The focus will be on the EDGAR database API provided by the SEC, and we'll explore how to fetch data, clean it, and return a pandas DataFrame.

## Talk Overview

In this session, we'll cover:

- **Introduction to the EDGAR Database API**: Understanding how to make requests to the SEC's EDGAR API.
- **Fetching Data**: How to retrieve data from the API.
- **Data Cleaning with Pandas**: Using pandas to clean and process the fetched data.
- **Creating DataFrames**: Converting the cleaned data into a pandas DataFrame for analysis.

## Agenda

### Introduction to EDGAR API:

- Overview of the API endpoints.
- How to authenticate and make requests.

### Data Retrieval:

- Demonstration of how to fetch data from the API.
- Example request and response handling.

### Data Cleaning:

- Using pandas to clean and transform the data.
- Examples of common data cleaning tasks.
- Discussion of major issues encountered with the data.

### Working with DataFrames:

- Converting cleaned data into a pandas DataFrame.
- Basic DataFrame operations for analysis.

## Code Walkthrough

### `edgar_api.py`

The main script that demonstrates how to fetch data from the EDGAR API, clean it using pandas, and return a DataFrame. This script will serve as a hands-on example during the talk.

### `alpha-vantage.py`

This script demonstrates how to get real-time stock information.

## Setup

To run the scripts, you'll need to set up your environment:

1. **Create a `.env` file** in the root directory of the project.
2. Add the following variables to your `.env` file:
   - `EMAIL_ADDRESS`: Your email address for accessing the EDGAR API.
   - `ALPHA_VANTAGE_API_KEY`: Your API key for Alpha Vantage. [Get your free API key here](https://www.alphavantage.co/support/#api-key).

Make sure not to share your `.env` file or commit it to version control to keep your API keys secure.
