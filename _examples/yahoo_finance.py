import yfinance as yf
import pandas as pd
# import yahooquery as yq
import json

# from tools.file_operations import read_data, write_data

def get_info(ticker: yf.Ticker) -> dict:
    """
    This function retrieves and returns detailed information about a stock ticker.

    Parameters:
    ticker (yf.Ticker): The yfinance Ticker object for the stock.

    Returns:
    dict: A dictionary containing detailed information about the stock.

    Note:
    The returned dictionary contains various attributes such as the stock's name,
    symbol, currency, country, etc.
    """

    # get ticker info
    info = ticker.info

    # basics = [info.shortName, info.zip,  info.longBusinessSummary, info.exchange, info.marketCap]
    # industry = [info.industry , info.industryKey, info.sector, info.sectorKey]
    # price_action = [info.previousClose, info.open, info.dayLow, info.dayHigh, info.volume]


    # show ISIN code
    # ISIN = International Securities Identification Number
    isin = ticker.isin
    
    # print(type(info))

    return info

def get_history(ticker: yf.Ticker, interval: str = "1d", time_period = "10y", store_path = None) -> tuple[pd.DataFrame, dict]:
    """
    Retrieves and processes historical data for a given stock.

    Parameters:
    ticker (yf.Ticker): The yfinance Ticker object for the stock.
    interval (str): The time interval for the historical data. Default is "1d" (daily).
    time_period (str): The time period for the historical data. Default is "10y" (10 years).
    store_path (str): The path to store the processed historical data. If not provided, the data will not be stored.

    Returns:
    Tuple[pd.DataFrame, dict]: A tuple containing the historical data as a DataFrame and the metadata as a dictionary.
    """
    # Fetch the historical data for the given stock
    hist = ticker.history(interval=interval, period=time_period)

    # Process the historical data if required
    # ...

    # Store the processed historical data if store_path is provided
    if store_path:
        file_operations.write_data(store_path, hist)

    # Prepare the metadata
    hist_meta = {
        "interval": interval,
        "time_period": time_period,
        "start_date": hist.index[0].strftime("%Y-%m-%d"),
        "end_date": hist.index[-1].strftime("%Y-%m-%d"),
        "columns": list(hist.columns)
    }

    # Return the historical data and metadata as a tuple
    return hist, hist_meta

def get_actions(ticker: yf.Ticker) -> pd.DataFrame:
    """
    Retrieves and returns a DataFrame containing future and historic earnings dates for the given stock.
    The function fetches at most the next 4 quarters and last 8 quarters by default.
    If more data is needed, the limit parameter can be increased.

    Parameters:
    ticker (yf.Ticker): The yfinance Ticker object for the stock.

    Returns:
    pd.DataFrame: A DataFrame containing the earnings dates.
    """

    # Show future and historic earnings dates, returns at most next 4 quarters and last 8 quarters by default.
    # Note: If more are needed use msft.get_earnings_dates(limit=XX) with increased limit argument.
    # earning_dates = ticker.get_earnings_dates(limit = 14)

    ac = ticker.actions # all actions available 
    # div = ticker.dividends # Return dividend section of actions
    # splits = ticker.splits # Return splits section of actions
    # cap_gains = ticker.capital_gains # only for mutual funds & etfs

    return ac

def income_sheet_fa(ticker: yf.Ticker, time_period: str) -> pd.DataFrame:
    """
    Generate a financial analysis report for the income statement.

    Parameters:
    ticker (yf.Ticker): The yfinance ticker object for the stock.
    time_period (str): The time period for the financial analysis. It can be 'annually' or 'quaterly'.

    Returns:
    income_stmt (pd.DataFrame): A DataFrame containing the financial analysis report for the income statement.

    Notes:
    - The function fetches the income statement data from the yfinance ticker object, prepares it for analysis, calculates additional features, and saves the final statement in an Excel file.
    - It also plots some useful information in a matplotlib figure.

    Definations:
    - Total Revenue = Operating Revenue(earnings from offering services or goods) + Non-Operating Revenue(earning from non-core businesses activities)
    - Costs of Goods Sold and Services Rendered (COGS) = Cost of goods and services in an income statement denote the expenses incurred to sell the final goods.
    - Gross Profit = Total Revenue - Costs of Goods Sold and Services Rendered (COGS)
    - Operating expenses (OPEX) = These denote costs linked to the goods and services offered by a business, such as rent, office, supplies etc
    - Earnings Before Interest, Taxes, Depreciation and Amortization (EBITDA) = EBITDA is the net income of a business after deducting interest, taxes, depreciation and amortization = Gross Profit - OPEX
    - Depreciation & Amortization (D&A) = These are special types of expenses that are spread over a long period. They include the decline in the value of equipment used in producing goods and services.
    - Earnings Before Tax (EBIT) = Operating Income/Profit = EBIDTA - D&A
    - Earnings Before Taxes(EBT) = EBIT - Intrest Expense
    - Net Income/PAT = EBT - Taxes
    """

    # get ticker from the yfinance ticker object
    sybl = ticker.ticker
    financial_dir = f"data/stocks/RELIANCE.NS/financials/"

    # to check if the right time period is passed
    if time_period == "annually":
        income_stmt_raw_T = ticker.income_stmt
    elif time_period == "quarterly":
        income_stmt_raw_T = ticker.quarterly_income_stmt
    else:
        print("Please enter a valid time period")
        exit()

    # Drop the empty values and transpose the matrix
    income_stmt_raw_T.dropna()
    income_stmt_raw = income_stmt_raw_T.T

    # save the raw data to files
    income_stmt_raw.to_excel(financial_dir + "income statement/raw.xlsx")

    # extract the useful features from the statement
    columns = [
        "Total Revenue",
        "Cost Of Revenue",
        "Gross Profit",
        "Operating Expense",
        "EBITDA",
        "Operating Income",
        "Pretax Income",
        "Tax Provision",
        "Net Income", 
        "Diluted Average Shares", 
        "Basic Average Shares"
        ]

    # pre-process the values to million dollar level
    income_stmt_final = income_stmt_raw[columns]
    for col in income_stmt_final.columns.values:
        income_stmt_final.loc[:, col] = income_stmt_final.loc[:, col] / 1000000

    # adding the EPS features
    income_stmt_final["Diluted EPS"] = income_stmt_final["Net Income"] / income_stmt_final["Diluted Average Shares"]
    income_stmt_final["Basic EPS"] = income_stmt_final["Net Income"] / income_stmt_final["Basic Average Shares"]

    # Adding some consolidated features
    income_stmt_final["TE"] = income_stmt_final["Total Revenue"] - income_stmt_final["Pretax Income"]
    income_stmt_final["OI"] = income_stmt_final["Pretax Income"] - income_stmt_final["Operating Income"]

    income_stmt_final.insert(6, "Other Income", income_stmt_final["OI"])
    income_stmt_final.insert(7, "Total Expenditure", income_stmt_final["TE"])

    income_stmt_final.drop(columns=['TE'], inplace=True)
    income_stmt_final.drop(columns=['OI'], inplace=True)

    # more readable labels
    income_stmt_final.rename(
        columns = {
            'Cost Of Revenue': 'Cost Of Goods Sold/COGS',
            "Operating Expense": "Operating Expense/OPEX",
            'Gross Profit': 'Gross Profit/Margin',
            "Operating Income" : "Operating Income/EBIT",
            "Net Income": "Net Income/PAT",
        }, 
        inplace=True
        )

    # save the final statement
    income_stmt_final.to_excel(financial_dir + "income statement/final.xlsx")

    return income_stmt_final

def balance_sheet_fa(ticker: yf.Ticker, time_period: str) -> pd.DataFrame:
    """
    This function generates a financial analysis report based on the balance sheet of a given stock.

    Parameters:
    ticker (yf.Ticker): The yfinance ticker object for the stock.
    time_period (str): The time period for the financial analysis. It can be either 'annually' or 'quaterly'.

    Returns:
    balance_sheet_final (pd.DataFrame): A DataFrame containing the financial analysis report for the balance sheet
    
    Notes:
    - The Balance Sheet is carried forward on basis of the defined time period.
    - An asset/liability is considered current if it can reasonably be converted into cash within one year. 
    - Assets
        -- Current
            --- Cash Cash Equivalents And Short Term Investments
            --- Inventory
            --- Accounts Receivable
        -- Non-Current 
            --- Accumulated Depreciation
            --- Net PPE
            --- Investments And Advances
    - Liabilities
        -- Current
            --- Accounts Payable
            --- Current Debt
            --- Current Deferred Liabilities
        -- Non-Current 
            --- Long Term Debt
            --- Other Non-Current Liabilities
    - Equity
        -- Stockholders Equity
        -- Retained Earnings
        -- Other Equity Adjustments
    """

    # Extract the stock symbol from the ticker object
    sybl = ticker.ticker
    financial_dir = f"data/stocks/{sybl}/financials/"

    # Check the time period and fetch the corresponding balance sheet data
    if time_period == "annually":
        balance_sheet_raw_T = ticker.balance_sheet
    elif time_period == "quarterly":
        balance_sheet_raw_T = ticker.quarterly_balance_sheet
    else:
        print("Please enter a valid time period")
        exit()

    # Clean the data by removing any NaN values
    balance_sheet_raw_T.dropna()
    balance_sheet_raw = balance_sheet_raw_T.T

    # save the raw data to files
    file_operations.write_data(financial_dir + "balance sheet/raw.xlsx", balance_sheet_raw)

    # Define the columns to include in the final balance sheet report
    columns = [
        "Total Assets",
        "Current Assets",
        "Cash And Cash Equivalents",
        "Cash Cash Equivalents And Short Term Investments",
        "Inventory",
        "Accounts Receivable",
        "Other Current Assets",
        "Total Non Current Assets",
        "Gross PPE",
        "Accumulated Depreciation",
        "Net PPE",
        "Investments And Advances",
        "Other Non Current Assets",
        "Total Liabilities Net Minority Interest",
        "Current Liabilities",
        "Accounts Payable",
        "Current Debt",
        "Current Deferred Liabilities",
        "Total Non Current Liabilities Net Minority Interest",
        "Long Term Debt",
        "Other Non Current Liabilities",
        "Stockholders Equity",
        "Common Stock",
        "Retained Earnings",
        "Other Equity Adjustments",
        ]

    # Create a new DataFrame with the selected columns
    balance_sheet_final = balance_sheet_raw[columns]

    # Convert the values in the DataFrame to millions for easier readability
    for col in balance_sheet_final.columns.values:
        balance_sheet_final.loc[:, col] = balance_sheet_final.loc[:, col] / 1000000

    # Rename specific columns for better readability
    balance_sheet_final.rename(
        columns = {
            'Other Short Term Investments' : 'Short Term Investments/Market Securities',
            'Total Liabilities Net Minority Interest' : 'Total Liabilities',
            'Total Non Current Liabilities Net Minority Interest' : 'Total Non-Current Liabilities',
            'Other Non Current Liabilities' : 'Other Non-Current Liabilities'
            }, 
        inplace=True
        )

    # Save the final balance sheet report to a file
    file_operations.write_data(financial_dir + "balance sheet/final.xlsx", balance_sheet_final)

    return balance_sheet_final

def cashflow_stmt_fa(ticker: yf.Ticker, time_period: str) -> pd.DataFrame:
    """
    This function generates a financial analysis report based on the cash flow statement of a given stock.

    Parameters:
    ticker (yf.Ticker): The yfinance ticker object for the stock.
    time_period (str): The time period for the financial analysis. It can be either 'annually' or 'quarterly'.

    Returns:
    pd.DataFrame: A DataFrame containing the final cash flow statement report.

    Notes:
    - The cash flow statement is carried forward on a timely basis.

    """

    # Extract the stock symbol from the ticker object
    sybl = ticker.ticker
    financial_dir = f"fin_bot/data/financials/stocks/{sybl}/financials/"

    # Check the time period and fetch the corresponding cash flow statement data
    if time_period == "annually":
        cashflow_raw_T = ticker.cashflow
    elif time_period == "quarterly":
        cashflow_raw_T = ticker.quarterly_cashflow
    else:
        print("Please enter a valid time period")
        exit()

    # Clean the data by removing any NaN values
    cashflow_raw_T.dropna()
    cashflow_raw = cashflow_raw_T.T

    # Save the raw cash flow statement data to a file
    file_operations.write_data(financial_dir + "cashflow/raw.xlsx", cashflow_raw)

    # Define the columns to include in the final cash flow statement report
    columns = [
        "Free Cash Flow",
        "Operating Cash Flow",
        "Net Income From Continuing Operations",
        "Depreciation And Amortization", 
        "Change In Working Capital",
        "Change In Receivables",
        "Change In Inventory",
        "Change In Payables And Accrued Expense",
        # "Change In Other Current Assets",
        # "Change In Other Current Liabilities",
        "Investing Cash Flow",
        "Purchase Of Investment",
        "Net PPE Purchase And Sale",
        "Sale Of Investment",
        # "Net Other Investing Changes",
        "Financing Cash Flow",
        "Net Common Stock Issuance",
        "Common Stock Dividend Paid",
        "Cash Dividends Paid",
        "Long Term Debt Payments",
        "Long Term Debt Issuance",
        "Net Other Financing Charges",
        ]

    # Create a new DataFrame with the selected columns
    cashflow_final = cashflow_raw[columns]

    # adding the Other Income feature
    cashflow_final["Other Income"] = cashflow_raw["Stock Based Compensation"] + cashflow_raw["Other Non Cash Items"]

    # Convert the values in the DataFrame to millions for easier readability
    for col in cashflow_final.columns.values:
        cashflow_final.loc[:, col] = cashflow_final.loc[:, col] / 1000000

    # Rename specific columns for better readability
    cashflow_final.rename(
        columns = {
            'Net Income From Continuing Operations' : 'Net Income',
            # Add this
            }, 
        inplace=True
        )

    # Save the final cash flow statement report to a file
    file_operations.write_data(financial_dir + "cashflow/final.xlsx", cashflow_final)

    return cashflow_final

def get_recommendations(ticker: yf.Ticker) -> pd.DataFrame:
    """
    Retrieves the recommendations made by analysts for the given stock.

    Parameters:
    ticker (yf.Ticker): The yfinance Ticker object for the stock.

    Returns:
    pd.DataFrame: A DataFrame containing the recommendations made by analysts.

    Note:
    This function currently only retrieves the recommendations made by analysts.
    Additional features such as a summary of recommendations or upgrade/downgrades
    are commented out and not included in the return value.
    """
    rec = ticker.get_recommendations()
    # rec_summ = ticker.recommendations_summary
    # updwn = ticker.upgrades_downgrades

    return rec

def get_options(ticker: yf.Ticker, store_path: str = None) -> dict:
    """
    Retrieves and processes option chain data for a given stock.

    Parameters:
    ticker (yf.Ticker): The yfinance Ticker object for the stock.
    store_path (str): The path to store the processed option chain data. If not provided, the data will not be stored.

    Returns:
    dict: A dictionary containing the option chain data for each expiration date.

    The function initializes an empty dictionary to store the option chains. It then defines the required columns for the option chain data.
    It iterates through the expiration dates of the options, downloads the option chain data for each date, filters and sorts the data based on the required columns, and stores the calls and puts data separately.
    Finally, it merges the calls and puts data, stores the option chain data in a dictionary, and optionally saves the data to Excel files.
    """
    # Initialize an empty dictionary to store the option chains dates
    options = ticker.options
    result = dict()

    # Define the required columns for the option chain data
    req_cols = ['strike', 'lastPrice', 'bid', 'ask',
    'change', 'percentChange', 'volume', 'openInterest']

    # Iterate through the expiration dates of the options
    for i in options:
        # Download the option chain data for the current expiration date
        opt = ticker.option_chain(i)

        # Filter and sort the option chain data based on required columns
        calls = opt.calls[req_cols]
        calls.set_index('strike', inplace=True)
        result[i] = [calls]

        puts = opt.puts[req_cols]
        puts.set_index('strike', inplace=True)
        result[i].append(puts)


        opt_chain = pd.merge(calls, puts, left_index=True, right_index=True, suffixes=('_call', '_put'))
        result[i].append(opt_chain)

    # Store the option chains in Excel files if store_path is provided
    if store_path:
            file_operations.write_data(store_path + f"{i}/call.xlsx", calls.sort_values(by = 'openInterest', ascending=False))
            file_operations.write_data(store_path + f"{i}/put.xlsx", puts.sort_values(by = 'openInterest', ascending=False))
            file_operations.write_data(store_path + f"{i}/options_chain.xlsx", opt_chain)

    # Return the option chains dictionary
    return result
    
def main():

    stock = "RELIANCE.NS"
    ticker = yf.Ticker(stock)

    # price_dir = f"fin_bot/data/crypto/BTC/prices/"
    # options_dir = f"fin_bot/data/stocks/{stock}/options/"

    # # Fetch and print company info
    # info = get_info(ticker)
    # # info = get_info(tickers.tickers["TSLA"])
    # print(json.dumps(info, indent=4))

    # # Fetch and print historical data for a time period
    # hist, hist_meta = get_history(ticker, time_period="max", store_path= price_dir + "historical.csv")

    # print(hist.columns.values)
    # # print(hist.head)
    # # print(hist.tail)
    # print(json.dumps(hist_meta, indent=4))

    # actions = get_actions(ticker)
    # print(actions.head)

    stmt = income_sheet_fa(ticker, "quarterly")
    # stmt = balance_sheet_fa(ticker, "annually")
    # stmt = cashflow_stmt_fa(ticker, "annually")
    print(stmt)

    # res = get_options(ticker, options_dir)

    # rec = get_recommendations(ticker)
    # rec = tradingview_tech_analysis(stock, exchange, country)
    # print(rec)

    # keywords = ["INE364U01010"]
    # k = yq.search(keywords, country="India")
    # print(json.dumps(k, indent=4))
    
  

if __name__ ==  "__main__":
    main()