import json
import pandas as pd
import requests
import os

from dotenv import load_dotenv

from Finances._tools import file_operations

# load environment variables from.env file for ALPHA_VANTAGE_API_KEY
load_dotenv()
alpha_vantage_api_key = os.getenv("ALPHA_API_KEY")

BASE_URL = "https://www.alphavantage.co/query?"

def request_agent(**kwargs) -> dict:
    """
    Sends a GET request to the Alpha Vantage API with the provided keyword arguments.
    Constructs the URL by appending the keyword arguments and the API key to the base URL.
    Sends a GET request to the constructed URL and parses the JSON response.

    Parameters:
    - kwargs (dict): Keyword arguments to be included in the API request. These arguments are appended to the base URL.
                      Each key-value pair in the dictionary represents a parameter and its corresponding value.

    Returns:
    - dict: The JSON response from the Alpha Vantage API as a dictionary. If the request fails, the function returns None.
    """
    # Base URL for Alpha Vantage API requests
    URL = "https://www.alphavantage.co/query?"

    # Add the passed keyword arguments to the URL
    for key, value in kwargs.items():
        if value is not None:
            URL += f"{key}={value}&"
    # Add the API key to the URL
    URL += f"apikey={alpha_vantage_api_key}"

    # Send a GET request to the URL
    print(f"> Requesting data from Alpha Vantage API at URL - {URL}")
    print("-" * 80)
    req = requests.get(URL)
    print(f"< Received data from Alpha Vantage API")
    print("-" * 80)

    # Parse the JSON response and return it as a dictionary
    if req.status_code == 200:
        try:
            data =  req.json()
            # print(data, type(data))
            return data
        except json.JSONDecodeError:
            print(f"Error occurred while parsing JSON response: {req.text}")
            return None
    else:
        print(f"Error occurred during API request: {req.status_code}")
        return None

def get_market_status(store_path: str = None) -> pd.DataFrame:
    """
    Retrieves market status information from the Alpha Vantage API.

    Parameters:
    - store_path (str, optional): The path to save the retrieved data as a CSV file. Defaults to None.

    Returns:
    - pd.DataFrame: A DataFrame containing the market status information.
                    If the 'markets' key does not exist in the API response, an empty DataFrame is returned.
                    If the 'store_path' is provided, the DataFrame is saved to a CSV file at the specified path.
    """
    # Query the `request_agent` function to get market status information
    data = request_agent(function="MARKET_STATUS")

    # If the 'markets' key exists in the response, convert it to a DataFrame and return it
    df = pd.DataFrame(data['markets']) if data else pd.DataFrame()

    # Store the new data with `equals` check with he old data.
    file_operations.write_data(store_path, df)

    return df

def get_gainers_losers() -> (pd.DataFrame, pd.DataFrame, pd.DataFrame):
    """
    Retrieves top gainers, losers, and most actively traded stocks from the Alpha Vantage API.

    Parameters:
    - None

    Returns:
    - df_gainers (pd.DataFrame): A DataFrame containing information about top gainers.
                                 Columns: '1. symbol', '2. name', '3. price', '4. volume', '5. percentage'.
    - df_losers (pd.DataFrame): A DataFrame containing information about top losers.
                                Columns: '1. symbol', '2. name', '3. price', '4. volume', '5. percentage'.
    - df_most_traded (pd.DataFrame): A DataFrame containing information about most actively traded stocks.
                                     Columns: '1. symbol', '2. name', '3. volume', '4. avg. daily volume', '5. market cap'.

    The function sends a GET request to the Alpha Vantage API with the 'TOP_GAINERS_LOSERS' function.
    It then parses the JSON response and converts the 'top_gainers', 'top_losers', and 'most_actively_traded' data to DataFrames.
    If the response data exists, the DataFrames are returned.
    If the response data is not available, empty DataFrames are returned and a message is printed.
    """
    # Query the `request_agent` function to get top gainers, losers, and most actively
    data = request_agent(function="TOP_GAINERS_LOSERS")

    # If the response data exists, convert it to DataFrames and return them
    if data:
        df_gainers = pd.DataFrame(data['top_gainers'])
        df_losers = pd.DataFrame(data['top_losers'])
        df_most_traded = pd.DataFrame(data['most_actively_traded'])
        # print(f"Top Gainers: {df_gainers.head()}")
        # print(f"Top Losers: {df_losers.head()}")
        # print(f"Most Actively Traded: {df_most_traded.head()}")

        return df_gainers, df_losers, df_most_traded
    else:
        print("No market status data available.")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

def get_news_and_sentiment(symbols: str, topics: str = None, time_period: list = [], sort: str = "RELEVANCE", limit : int = 0, store_path: str = None) -> pd.DataFrame:
    """
    Retrieves news and sentiment information for a given list of ticker symbols.

    Parameters:
    - symbols (str): A string containing comma-separated ticker symbols for which to retrieve news and sentiment information.
    - topics (str, optional): A string containing comma-separated topics to filter news articles. Defaults to None.
    - time_period (list, optional): A list of two strings representing the start and end dates for filtering news articles. Defaults to an empty list.
    - sort (str, optional): The sorting order of news articles. Accepted values: "RELEVANCE", "POPULARITY", "PUBLISHED". Defaults to "RELEVANCE".
    - limit (int, optional): The maximum number of news articles to retrieve. Defaults to 0, which means all available articles will be retrieved.
    - store_path (str, optional): The path to save the retrieved data as an Excel file. Defaults to None.

    Returns:
    - pd.DataFrame: A DataFrame containing the news and sentiment information for the specified ticker symbols.
                    If the 'store_path' is provided, the DataFrame is saved to an Excel file at the specified path.
                    If the response data is not available, an empty DataFrame is returned.
    """
    # Query the `request_agent` function to get news and sentiment information
    data = request_agent(function="NEWS_SENTIMENT", tickers=symbols, sort=sort)
    # print(data.keys())

    # If the response data exists, convert it to a DataFrame and return it
    df = pd.DataFrame(data['feed']) if data else pd.DataFrame()

    # Store the new data with `equals` check with he old data.
    file_operations.write_data(store_path, df)

    return df

def find_ticker(keywords: str, store_path: str = None) -> pd.DataFrame:
    """
    This function retrieves ticker symbols based on the provided keywords using the Alpha Vantage API.
    It sends a GET request to the API with the 'SYMBOL_SEARCH' function and the provided keywords.
    The function then parses the JSON response and converts the 'bestMatches' data to a DataFrame.
    If a store_path is provided, the DataFrame is saved to a CSV file at the specified path.

    Parameters:
    - keywords (str): The keywords to search for ticker symbols.
    - store_path (str, optional): The path to save the DataFrame as a CSV file. Defaults to None.

    Returns:
    - pd.DataFrame: A DataFrame containing the ticker symbols and their corresponding information.
    """
    # Query the `request_agent` function to find ticker symbols based on the provided keywords
    data = request_agent(function="SYMBOL_SEARCH", keywords=keywords)

    # If the 'bestMatches' key exists in the response, convert it to a DataFrame and return it
    df = pd.DataFrame(data['bestMatches']) if data else pd.DataFrame()

    # Store the new data with `equals` check with he old data.
    file_operations.write_data(store_path, df)

    return df
    
def get_global_quote(sybl: str, store_path: str = None) -> pd.DataFrame:
    """
    Retrieves global quote information for a given ticker symbol using the Alpha Vantage API.

    Parameters:
    - sybl (str): The ticker symbol for which to retrieve global quote information.
    - store_path (str, optional): The path to save the retrieved data as a CSV file. Defaults to None.

    Returns:
    - pd.DataFrame: A DataFrame containing the global quote information for the specified ticker symbol.
                    If the 'Global Quote' key does not exist in the API response, an empty DataFrame is returned.
                    If the 'store_path' is provided, the DataFrame is saved to a CSV file at the specified path.
    """
    # Query the `request_agent` function to get global quote information for the provided ticker symbol
    data = request_agent(function="GLOBAL_QUOTE", symbol=sybl)

    # If the 'Global Quote' key exists in the response, convert it to a DataFrame and return it
    df = pd.DataFrame(data['Global Quote']) if data else pd.DataFrame()

    # Store the new data with `equals` check with he old data.
    file_operations.write_data(store_path, df)

    return df

def get_stock_price_data(sybl: str, time_period: str = "daily",  outputsize: str = None, datatype: str = None, store_path = None) -> pd.DataFrame:
    """
    Retrieves historical stock price data for a given ticker symbol and time period.

    Parameters:
    - sybl (str): The ticker symbol for which to retrieve stock price data.
    - time_period (str, optional): The time period for which to retrieve data. Defaults to "daily".
                                  Accepted values: "daily", "weekly", "monthly".
    - outputsize (str, optional): The size of the output. Defaults to None.
                                  Accepted values: "compact" (100 data points), "full" (all available data points).
    - datatype (str, optional): The type of data to retrieve. Defaults to None.
                               Accepted values: "json" (JSON format), "csv" (CSV format).
    - store_path (str, optional): The path to save the retrieved data as a CSV file. Defaults to None.

    Returns:
    - pd.DataFrame: A DataFrame containing the historical stock price data for the specified ticker symbol and time period.
                    If the 'store_path' is provided, the DataFrame is saved to a CSV file at the specified path.
    """
    # Basic legends to define the API function to make the request
    time_period_legends = {
        "daily": ["TIME_SERIES_DAILY", 'Time Series (Daily)'],
        "weekly": ["TIME_SERIES_WEEKLY", 'Time Series (Weekly)'],
        "monthly": ["TIME_SERIES_MONTHLY", 'Time Series (Monthly)'],
    }

    # Build the base URL for the selected time series type and make the request
    data = request_agent(function=time_period_legends[time_period][0], symbol=sybl, outputsize=outputsize, datatype=datatype)

    # If the data is available, convert it to a DataFrame and return it
    df = pd.DataFrame(data[time_period_legends[time_period][1]]).T if data else pd.DataFrame()
    
    # Set the index name as Date: with datetime format
    df.index = pd.to_datetime(df.index)
    df.index.name = "Date"

    # Set the columns names as 'Open', 'High', 'Low', 'Close', 'Volume'
    df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

    # # uncomment this line if you want to save the raw data locally
    # print(df.head())
    file_operations.write_data(os.path.dirname(store_path) + 'daily_prices_alpha_raw.xlsx', df)

    # Get the processed price data in descending order od index `Date` with proper columns
    history_processed = other_funcs.process_data(df)

    # save the data locally
    file_operations.write_data(store_path, df)

    return df

def get_stock_financials(statement_type: str, sybl: str, time_period: str, store_path: str = None) -> pd.DataFrame:
    """
    Retrieves financial statement data for a given ticker symbol, statement type, and time period.

    Parameters:
    - statement_type (str): The type of financial statement to retrieve. Accepted values: "income", "balance", "cashflow".
    - sybl (str): The ticker symbol for which to retrieve financial statement data.
    - time_period (str): The time period for which to retrieve data. Accepted values: "annual", "quarterly".
    - store_path (str, optional): The path to save the retrieved data as a CSV file. Defaults to None.

    Returns:
    - pd.DataFrame: A DataFrame containing the financial statement data for the specified ticker symbol, statement type, and time period.
                    If the 'store_path' is provided, the DataFrame is saved to a CSV file at the specified path.
    """
    # Select the appropriate financial statement type based on the input type (income, balance, cashflow)
    statement_legends = {
        "income": "INCOME_STATEMENT",
        "balance": "BALANCE_SHEET",
        "cashflow": "CASH_FLOW",
    }

    # Query the `request_agent` function to get financial statement information for the provided ticker symbol and time period
    data = request_agent(function=statement_legends[statement_type], symbol=sybl)
    # print(data['Information'])

    # Convert the response to a DataFrame and transpose it based on the selected time period (annual or quarterly)
    df = pd.DataFrame()
    if time_period == "annual":   
        df = pd.DataFrame(data['annualReports'])
    elif time_period == "quarterly":
        df = pd.DataFrame(data['annualReports'])

    df.set_index('fiscalDateEnding', inplace=True)

    # Store the new data with `equals` check with he old data.
    if store_path:
        file_operations.write_data(store_path, df)

    return df

def get_options_chain(sybl: str, store_path: str = None) -> dict:
    """
    Retrieves historical options chain information for a given ticker symbol.

    Parameters:
    sybl (str): The ticker symbol for which to retrieve historical options chain information.
    store_path (str, optional): The path to save the retrieved data as Excel files. Defaults to None.

    Returns:
    dict: A dictionary containing the options chain data for each expiration date.
          Each entry in the dictionary is a list containing three DataFrames:
          - The options chain data for all strikes and types.
          - The options chain data for calls.
          - The options chain data for puts.
    """
    # Query the `request_agent` function to get historical options chain information for the provided ticker symbol
    data = request_agent(function="HISTORICAL_OPTIONS", symbol=sybl)
    df_opt_chain = pd.DataFrame(data['data'])

    # Useful columns for the options chain
    useful_columns = ['expiration', 'strike', 'type', 'last', 'mark', 'bid', 'ask', 'volume', 'open_interest', 'implied_volatility', 'delta', 'gamma', 'theta', 'vega', 'rho']
    results = dict()

    # Filter the columns for useful column and create separate DataFrames for calls and puts
    df_opt_chain = df_opt_chain[useful_columns]
    df_calls = df_opt_chain[df_opt_chain['type'] == 'call']
    df_puts = df_opt_chain[df_opt_chain['type'] == 'put']

    # Get unique values for the `expiration` column
    options = df_calls['expiration'].unique()

    for i in options:
        # Filter the options chain for the current expiration date
        opt_chain = df_opt_chain[df_opt_chain['expiration'] == i]
        opt_chain = opt_chain.drop(columns = ['expiration'])
        opt_chain.set_index('strike', inplace=True)
        results[i] = [opt_chain]

        calls = df_calls[df_calls['expiration'] == i]
        calls.set_index('strike', inplace=True)
        calls = calls.drop(columns=['type', 'expiration'])
        results[i].append(calls)

        puts = df_puts[df_puts['expiration'] == i]
        puts.set_index('strike', inplace=True)
        puts = puts.drop(columns=['type', 'expiration'])
        results[i].append(puts)

        # Store the option chains in Excel files if store_path is provided
        if store_path:
                file_operations.write_data(store_path + f"{i}/call.xlsx", calls)
                file_operations.write_data(store_path + f"{i}/put.xlsx", puts)
                file_operations.write_data(store_path + f"{i}/options_chain.xlsx", opt_chain)

    return results
    
def main():

    # # proper key import check
    # print(alpha_vantage_api_key)

    sybl = "AAPL"

    market_store = "fin_bot/data/market/"
    price_dir = f"fin_bot/data/stocks/{sybl}/prices/"
    options_dir = f"fin_bot/data/stocks/{sybl}/options/"
    financial_store = f"fin_bot/data/stocks/{sybl}/financials/"
    news_store = f"fin_bot/data/news/alpha_vantage/{sybl}/"

    # Example usage:
    res =  find_ticker("reliance")
    # res = get_global_quote(ticker)
    # res = get_market_status()
    # res = get_gainers_losers()
    # res = get_stock_price_data(ticker, "daily", store_path=price_dir+"daily_prices_alpha_raw.xlsx")
    # res = get_stock_financials("cashflow", sybl, "annual", financial_store + "cashflow/cashflow.xlsx")
    # res = get_news_and_sentiment(ticker,store_path= news_store + "news.xlsx")
    
    # res = get_options_chain(ticker, options_dir)

    
    print(type(res))
    res.to_excel("./trial.xlsx")
    # print(res.keys())
    # print(res[list(res.keys())[0]][1].head())


    # df = pd.read_excel('fin_bot/data/stocks/AAPL/financials/income_statement.xlsx')

    # print(df.head())
    # print(df.info())


if __name__ == "__main__":
    main()