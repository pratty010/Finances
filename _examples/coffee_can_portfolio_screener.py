import yfinance as yf
import pandas as pd
import json

from Finances._tools.file_operations import read_data

def check_valid_existence(info: dict, sybl: str) -> bool:
    """
    Check if a company has existed for at least 11 years.

    This function determines whether a company has been trading for a minimum of 11 years
    based on its first trading date. It also prints information about the check process.
    Parameters:
    info (dict): A dictionary containing financial information about the company.
                 It must include a 'firstTradeDateEpochUtc' key representing the first
                 trading date of the company in Unix timestamp format.
    sybl (str): The stock symbol or ticker of the company being checked.

    Returns:
    bool: True if the company has existed for at least 11 years, False otherwise.
          When True, it also prints the company symbol and its first traded date.
    """

    # Check if company has existed for at least 11 years (>10)
    first_traded_date = pd.to_datetime(info['firstTradeDateEpochUtc']).date()
    date_today = pd.to_datetime('today').date()
    print(f"> Checking if {sybl} has existed for at least 11 years...")
    print('-' * 80)
    if (date_today - first_traded_date).days > 11 * 365:
        print(f"{sybl} has existed for at least 11 years. Moving forward")
        print(f"First Traded Date: {first_traded_date}")
        print("-" * 80)
        return True
    else:
        return False

def do_market_cap_check(info: dict, sybl: str) -> bool:
    """
    Check if a company's market capitalization meets the criteria for coffee can investing.

    This function evaluates whether a company's market capitalization satisfies specific
    thresholds based on its currency. It supports USD and INR currencies.
    Parameters:
    info (dict): A dictionary containing financial information about the company.
                 It must include keys 'currency' and 'marketCap' representing the
                 company's currency and market capitalization respectively.
    sybl (str): The stock symbol or ticker of the company being checked.

    Returns:
    bool: True if the company's market capitalization meets the criteria, False otherwise.
          When True, it also prints the company symbol and its market capitalization.
    """
    # extract currency and market cap from the financial information dictionary
    curr = info["currency"]
    market_cap = info["marketCap"]

    # check market cap based on currency
    print(f"> Checking if {sybl} meets the m-cap criteria...")
    print('-' * 80)
    if curr == "USD" and market_cap / 1000000000 > 10:
        m_cap = market_cap / 1000000000
        print(f"{sybl} has a market cap of {m_cap} Billion USD. Moving forward")
        print("-" * 80)
        return True
    elif curr == "INR" and market_cap / 10000000 > 100:
        m_cap = market_cap / 10000000
        print(f"{sybl} has a market cap of {m_cap} Cr INR. Moving forward")
        print("-" * 80)
        return True
    else:
        # to do for other major currencies
        return False

def do_rev_growth_check(sybl: str) -> bool:
    """
    This function checks if a company's average revenue growth over the last 10 years is above 10%.
    It reads the income statement data from an Excel file and calculates the average revenue growth.

    Parameters:
    sybl (str): The symbol of the company to check.

    Returns:
    bool: True if the average revenue growth over the last 10 years is above 10%, False otherwise.
          If True, it prints a message indicating the company's revenue growth and moves forward.
    """
    # define the file path for income statement data and read it
    income_path = f"fin_bot/data/stocks/{sybl}/financials/income statement/income_statement.xlsx"
    income_df = read_data(income_path, index='fiscalDateEnding')
    # print(income_df.columns)

    # calculate revenue growth over the last 10 years
    revenue = income_df[["totalRevenue"]].sort_index(ascending=True)
    revenue['revenue growth'] = revenue["totalRevenue"].pct_change() 
    # print(revenue.sort_index(ascending=False))

    # calculate average revenue growth over the last 10 years
    avg_revenue_growth_10YRs = revenue['revenue growth'].head(10).mean().round(2) * 100

    # check if average revenue growth over the last 10 years is above 10% to meet the criteria for coffee can investing
    print("> Checking if {ticker} meets the revenue growth criteria...")
    print('-' * 80)
    if avg_revenue_growth_10YRs > 10:
        print(f"{sybl} has a revenue growth of {avg_revenue_growth_10YRs}% over the last 10 years. Moving forward...")
        print("-" * 80)
        return True
    else:
        return False
    
def do_ROCE_check(sybl: str) -> bool:
    """
    This function checks if a company's Return on Capital Employed (ROCE) over the last 10 years is above 15%.
    It reads the income statement and balance sheet data from Excel files and calculates the ROCE.

    Parameters:
    sybl (str): The symbol of the company to check.

    Returns:
    bool: True if the average ROCE over the last 10 years is above 15%, False otherwise.
          If True, it prints a message indicating the company's ROCE and moves forward.
    """
    # define the file path for income statement and balance sheet data and read it
    income_path = f"fin_bot/data/stocks/{sybl}/financials/income statement/income_statement.xlsx"
    balance_file = f"fin_bot/data/stocks/{sybl}/financials/balance sheet/balance_sheet.xlsx"
    income_df = read_data(income_path, index='fiscalDateEnding')
    balance_df = read_data(balance_file, index='fiscalDateEnding')
    # print(income_df.columns)
    # print(balance_df.columns)

    # calculate ROCE from income statement data and balance sheet data
    ROCE_df = income_df[["ebit"]].copy()
    ROCE_df["Total_Assets"] = balance_df["totalAssets"]
    ROCE_df["Current_Liabilities"] = balance_df["totalCurrentLiabilities"] 
    # print(ROCE_df)

    ROCE_df["Capital_Employed"] = ROCE_df["Total_Assets"] - ROCE_df["Current_Liabilities"]
    ROCE_df["ROCE"] = (ROCE_df["ebit"] / ROCE_df["Capital_Employed"]) * 100


    # calculate average ROCE over the last 10 years to meet the criteria for coffee can investing
    print("> Checking if {ticker} meets the ROCE criteria...")
    print('-' * 80)  # Printing separator line for better readability
    ROCE_10yrs = ROCE_df["ROCE"].head(10).mean().round(2)
    if ROCE_10yrs > 15:
        print(f"{sybl} has a ROCE of {ROCE_10yrs}% over the last 10 Years. Moving forward")
        print("-" * 80)
        return True
    else:
        return False

def coffee_can_eligible(sybl: str) -> bool:
    """
    This function retrieves financial parameters of a company and checks if it meets the criteria for coffee can investing.

    Parameters:
    sybl (str): The symbol of the company to check.

    Returns:
    bool: True if the company meets all the criteria for coffee can investing, False otherwise.
          If True, it prints a message indicating the company's name and its successful addition to the portfolio.
          If False, it prints a message indicating the company's name and its failure to meet the criteria.
    """

    # Fetch company information using yfinance API
    co_info = yf.Ticker(sybl).info

    # Check if the company has existed for at least 11 years
    existence = check_valid_existence(co_info, sybl)
    if existence:
        # Check if the company's market capitalization, revenue growth, and ROCE growth meet the criteria for coffee can investing
        if do_market_cap_check(co_info, sybl) and do_rev_growth_check(sybl) and do_ROCE_check(sybl):
            print(f"> {sybl} meets all the criteria to be added to the coffee can investing Portfolio.")
            print("-" * 80)
            return True
        else:
            return False

    else:
        print(f"> {sybl} does not meet the criteria for a coffee can.")
        print("-" * 80)
        return False

def main():

    sybl = "AAPL"  # Example: Apple Inc.

    res = coffee_can_eligible(sybl)
    print(res)


if __name__ == "__main__":
    main()