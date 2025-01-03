from nsepython import nse_get_index_list, nsefetch
import pandas as pd
import os
import json

# Function to fetch data directly using nsefetch
def get_index_stocks(index_name):
    """
    Fetches stock data for a given index from the NSE (National Stock Exchange) API.

    This function constructs the API URL for the specified index, fetches the data,
    and processes it to return a pandas DataFrame containing relevant stock information.

    Parameters:
    index_name (str): The name of the index for which to fetch stock data.

    Returns:
    pandas.DataFrame: A DataFrame containing stock data with columns:
        - ISIN: International Securities Identification Number
        - Symbol: Stock symbol
        - Industry: Industry classification
        - Current: Last traded price
        - Open: Opening price
        - Close: Previous day's closing price
        - Year High: 52-week high price
        - Year Low: 52-week low price
        - Near Weak High: Near week high price
        - Near Weak Low: Near week low price

    If an error occurs during the process, an empty DataFrame is returned.
    """
    try:
        # Construct the API URL for index constituents
        url = f"https://www.nseindia.com/api/equity-stockIndices?index={index_name}"
        # print(url)

        # Fetch the data
        index_data = nsefetch(url)  # nsefetch handles NSE's headers and cookies
        # print(json.dumps(index_data["data"][1], indent=4))

        # Parse and extract stock data
        if "data" in index_data:
            data = index_data["data"]
            stocks_data = [
                {"ISIN" : stock["meta"]["isin"],
                 "Symbol" : stock["symbol"],
                 "Industry" : stock["meta"]["industry"],
                 "Current" : stock["lastPrice"],
                 "Open" : stock["open"],
                 "Close" : stock["previousClose"],
                 "Year High" : stock["yearHigh"],
                 "Year Low" : stock["yearLow"],
                 "Near Weak High" : stock["nearWKH"],
                 "Near Weak Low" : stock["nearWKL"],
                       }
                       for stock in data[1:]
                       ]
            # Convert the list of dictionaries to a DataFrame
            return(pd.DataFrame(stocks_data))
        else:
            raise ValueError(f"Failed to fetch data for index: {index_name}")
    except Exception as e:
        print(f"Error: {e}")
        return pd.DataFrame()

def get_52w_losers_gainers(stocks_data):
    """
    Analyze stock data to identify 52-week losers and gainers based on predefined percentage thresholds.

    This function calculates the total year-to-date loss and gain for each stock,
    identifies stocks that have lost more than 25% or gained more than 30% in the past year,
    and sorts them accordingly.

    Parameters:
    stocks_data (pandas.DataFrame): A DataFrame containing stock data with columns:
        - Current: Last traded price
        - Year High: 52-week high price
        - Year Low: 52-week low price
        (and other columns as defined in the get_index_stocks function)

    Returns:
    tuple: A tuple containing three pandas DataFrames:
        - stocks_data: The original DataFrame with additional columns for total year down and up percentages
        - losers: A DataFrame of stocks that have lost more than 25% in the past year, sorted by loss percentage
        - gainers: A DataFrame of stocks that have gained more than 30% in the past year, sorted by gain percentage
    """
    # Define the percentage of loss for losers
    percentage_loss = 25
    # Define the percentage of gain for gainers
    percentage_gain = 30

    # Filter stocks where gain is more than the defined percentage

    # Add Loss data as 1 - current price/year high
    # Add 
    stocks_data["Total Year Down"] = (1 - (stocks_data["Current"] / stocks_data["Year High"])) * 100
    stocks_data["Total Year Up"] = ((stocks_data["Current"] / stocks_data["Year Low"]) - 1) * 100
    # print(stocks_data)

    # Filter stocks where loss is more than the defined percentage
    losers = stocks_data[stocks_data["Total Year Down"] > percentage_loss]

    # Filter stocks where gain is more than the defined percentage
    gainers = stocks_data[stocks_data["Total Year Up"] > percentage_gain]

    # Sort losers by loss percentage in descending order
    losers = losers.sort_values(by=["Total Year Down", "Total Year Up"], ascending= [False, True])

    # Sort gainers by gain percentage in descending order
    gainers = gainers.sort_values(by=["Total Year Up", "Total Year Down"], ascending= [False, True])

    # Only keep important columns for losers and gainers
    columns = ["ISIN", "Symbol", "Industry", "Current", "Year High", "Year Low", "Total Year Down", "Total Year Up"]
    losers = losers[columns]
    gainers = gainers[columns]

    # Return the stocks data and losers
    return stocks_data, losers, gainers

def main():

    # Fetch list of indices from NSE API and choose a specific index
    indices = nse_get_index_list()
    index = "NIFTY 100"
    index_data_path = f"fin_bot/data/indices/{index}_stocks.xlsx"

    # stocks_data = get_index_stocks(index)

    # Check if data already exists
    if os.path.exists(index_data_path):
        print("Data already exists")
        stocks_data = pd.read_excel(index_data_path)
    else:
        # If not, fetch data and save it
        print(f"Fetching data for {index}")
        stocks_data = get_index_stocks(index)
        stocks_data.to_excel(index_data_path, index=False)
    print(stocks_data)

    # Get losers and gainers
    stocks_data, losers, gainers = get_52w_losers_gainers(stocks_data)
    print(losers)
    print(gainers)

    # Save losers to a separate file
    losers.to_excel(f"fin_bot/data/indices/{index}_losers.xlsx", index=False)
    # Save gainers to a separate file
    gainers.to_excel(f"fin_bot/data/indices/{index}_gainers.xlsx", index=False)


if __name__ == "__main__":
    main()