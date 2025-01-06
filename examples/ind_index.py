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

    # Add Loss data as 1 - current price/year high and to high profit %
    # Add Up data as current price/year low - 1
    stocks_data["Total Year Down"] = (1 - (stocks_data["Current"] / stocks_data["Year High"])) * 100
    stocks_data["To Year High Profit"] = ((stocks_data["Year High"] / stocks_data["Current"]) - 1) * 100
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
    columns = ["ISIN", "Symbol", "Industry", "Current", "Year High", "Year Low", "Total Year Down", "To Year High Profit",  "Total Year Up"]
    losers = losers[columns]
    gainers = gainers[columns]

    # Return the stocks data and losers
    return stocks_data, losers, gainers

def main():

    # Fetch list of indices from NSE API and choose a specific index
    # indices = nse_get_index_list()
    # print(indices)

    # ['NIFTY 50', 'NIFTY NEXT 50', 'NIFTY IT', 'NIFTY BANK', 'INDIA VIX', 'NIFTY 100', 'NIFTY 500', 'NIFTY MIDCAP 100', 'NIFTY MIDCAP 50', 'NIFTY INFRA', 'NIFTY REALTY', 'BHARATBOND-APR30', 'NIFTY FMCG', 'NIFTY GS 8 13YR', 'NIFTY IND DIGITAL', 'NIFTY MICROCAP250', 'NIFTY MOBILITY', 'NIFTY MS IT TELCM', 'NIFTY NEW CONSUMP', 'NIFTY PSE', 'NIFTY TRANS LOGIS', 'NIFTY100 LOWVOL30', 'NIFTY200 VALUE 30', 'NIFTY50 VALUE 20', 'NIFTY500 EW', 'NIFTY ALPHALOWVOL', 'NIFTY ENERGY', 'NIFTY IND TOURISM', 'NIFTY M150 QLTY50', 'NIFTY MIDCAP 150', 'NIFTY MS FIN SERV', 'NIFTY NONCYC CONS', 'NIFTY PSU BANK', 'NIFTY SML250 Q50', 'NIFTY SMALLCAP 250', 'NIFTY TOP 10 EW', 'NIFTY100 ENH ESG', 'NIFTY50 PR 2X LEV', 'NIFTY50 TR 1X INV', 'NIFTY 200', 'NIFTY AQL 30', 'NIFTY COREHOUSING', 'NIFTY CORP MAATR', 'NIFTY MID LIQ 15', 'NIFTY PVT BANK', 'NIFTY SERV SECTOR', 'NIFTY SHARIAH 25', 'NIFTY100 ESG', 'NIFTY100 LIQ 15', 'NIFTY100ESGSECLDR', 'NIFTY500MOMENTM50', 'BHARATBOND-APR31', 'NIFTY AUTO', 'NIFTY CONSUMPTION', 'NIFTY EV', 'NIFTY FINSEREXBNK', 'NIFTY GS 10YR CLN', 'NIFTY GS 11 15YR', 'NIFTY GS COMPSITE', 'NIFTY HIGHBETA 50', 'NIFTY IND DEFENCE', 'NIFTY INDIA MFG', 'NIFTY LOW VOL 50', 'NIFTY METAL', 'NIFTY MS IND CONS', 'NIFTY MULTI INFRA', 'NIFTY MULTI MFG', 'NIFTY QLTY LV 30', 'NIFTY SMALLCAP 50', 'NIFTY TOP 20 EW', 'NIFTY200 ALPHA 30', 'NIFTY50 TR 2X LEV', 'BHARATBOND-APR33', 'NIFTY ALPHA 50', 'NIFTY AQLV 30', 'NIFTY COMMODITIES', 'NIFTY DIV OPPS 50', 'NIFTY FINSRV25 50', 'NIFTY GROWSECT 15', 'NIFTY HEALTHCARE', 'NIFTY MID SELECT', 'NIFTY OIL AND GAS', 'NIFTY500 SHARIAH', 'NIFTYMS400 MQ 100', 'BHARATBOND-APR32', 'INDEX1 NSETEST', 'INDEX2 NSETEST', 'NIFTY CAPITAL MKT', 'NIFTY GS 10YR', 'NIFTY GS 15YRPLUS', 'NIFTY MEDIA', 'NIFTY MULTI MQ 50', 'NIFTY RURAL', 'NIFTY100 ALPHA 30', 'NIFTY50 DIV POINT', 'BHARATBOND-APR25', 'NIFTY CONSR DURBL', 'NIFTY CPSE', 'NIFTY FIN SERVICE', 'NIFTY GS 4 8YR', 'NIFTY IPO', 'NIFTY MIDSMALLCAP 400', 'NIFTY MIDSML HLTH', 'NIFTY MNC', 'NIFTY SMLCAP 100', 'NIFTY INDIA CORPORATE GROUP INDEX - TATA GROUP 25 CAP', 'NIFTY TOP 15 EW', 'NIFTY200 QUALTY30', 'NIFTY50 PR 1X INV', 'NIFTY500 LMS EQL', 'NIFTYSML250MQ 100', 'NIFTY HOUSING', 'NIFTY LARGEMID250', 'NIFTY PHARMA', 'NIFTY TOTAL MKT', 'NIFTY100 EQL WGT', 'NIFTY100 QUALTY30', 'NIFTY200 MOMENTM30', 'NIFTY50 EQL WGT', 'NIFTY50 SHARIAH', 'NIFTY500 MULTICAP', 'Nifty Midcap150 Momentum 50', 'NIFTY 50 FUTURES INDEX', 'NIFTY 50 ARBITRAGE', 'NIFTY INDIA CORPORATE GROUP INDEX - MAHINDRA GROUP', 'NIFTY INDIA CORPORATE GROUP INDEX - ADITYA BIRLA GROUP', 'NIFTY INDIA CORPORATE GROUP INDEX - TATA GROUP', 'NIFTY SME EMERGE', 'NIFTY REITS & INVITS', 'NIFTY INDIA RAILWAYS PSU', 'NIFTY500 QUALITY 50', 'NIFTY500 LOW VOLATILITY 50', 'NIFTY50 USD', 'NIFTY 1D RATE INDEX', 'NIFTY BHARAT BOND INDEX - APRIL 2030', 'NIFTY 10 YEAR SDL INDEX', 'NIFTY BHARAT BOND INDEX - APRIL 2025', 'NIFTY BHARAT BOND INDEX - APRIL 2031', 'NIFTY PSU BOND PLUS SDL APR 2026 50:50 INDEX', 'NIFTY SDL APR 2026 TOP 20 EQUAL WEIGHT INDEX', 'NIFTY AAA BOND PLUS SDL APR 2026 50:50 INDEX', 'NIFTY SDL PLUS PSU BOND SEP 2026 60:40 INDEX', 'NIFTY PSU BOND PLUS SDL SEP 2027 40:60 INDEX', 'NIFTY PSU BOND PLUS SDL APR 2027 50:50 INDEX', 'NIFTY AAA BOND PLUS SDL APR 2026 70:30 INDEX', 'NIFTY AAA BOND PLUS SDL APR 2031 70:30 INDEX', 'NIFTY BHARAT BOND INDEX - APRIL 2032', 'NIFTY CPSE BOND PLUS SDL SEP 2026 50:50 INDEX', 'NIFTY SDL APR 2027 INDEX', 'NIFTY SDL APR 2027 TOP 12 EQUAL WEIGHT INDEX', 'NIFTY SDL APR 2032 TOP 12 EQUAL WEIGHT INDEX', 'NIFTY SDL PLUS G-SEC JUN 2028 30:70 INDEX', 'NIFTY SDL PLUS AAA PSU BOND DEC 2027 60:40 INDEX', 'NIFTY SDL JUN 2027 INDEX', 'NIFTY SDL SEP 2027 INDEX', 'NIFTY AAA CPSE BOND PLUS SDL APR 2027 60:40 INDEX', 'NIFTY SDL SEP 2025 INDEX', 'NIFTY SDL DEC 2028 INDEX', 'NIFTY SDL PLUS AAA PSU BOND JUL 2028 60:40 INDEX', 'NIFTY AAA PSU BOND PLUS SDL APR 2026 50:50 INDEX', 'NIFTY AAA PSU BOND PLUS SDL SEP 2026 50:50 INDEX', 'NIFTY SDL PLUS AAA PSU BOND JUL 2033 60:40 INDEX', 'NIFTY SDL PLUS G-SEC JUN 2028 70:30 INDEX', 'NIFTY SDL SEP 2026 INDEX', 'NIFTY BHARAT BOND INDEX - APRIL 2033', 'NIFTY SDL SEP 2026 V1 INDEX', 'NIFTY SDL JUL 2026 INDEX', 'NIFTY SDL DEC 2026 INDEX', 'NIFTY SDL PLUS G-SEC SEP 2027 50:50 INDEX', 'NIFTY SDL PLUS AAA PSU BOND APR 2026 75:25 INDEX', 'NIFTY SDL PLUS G-SEC JUN 2029 70:30 INDEX', 'NIFTY SDL JUL 2033 INDEX', 'NIFTY SDL OCT 2026 INDEX', 'NIFTY SDL PLUS AAA PSU BOND APR 2028 75:25 INDEX', 'NIFTY SDL PLUS G-SEC JUNE 2027 40:60 INDEX', 'NIFTY SDL JUL 2028 INDEX', 'NIFTY SDL JUNE 2028 INDEX', 'NIFTY 3 YEAR SDL INDEX', 'NIFTY 5 YEAR SDL INDEX', 'NIFTY AAA BOND JUN 2025 HTM INDEX', 'NIFTY AQLV 30 PLUS 5YR G-SEC 70:30 INDEX', 'NIFTY MULTI ASSET - EQUITY : DEBT : ARBITRAGE : REITS/INVITS (50:20:20:10) INDEX', 'NIFTY MULTI ASSET - EQUITY : ARBITRAGE : REITS/INVITS (50:40:10) INDEX', 'NIFTY 5YR BENCHMARK G-SEC INDEX', 'NIFTY INDIA GOVERNMENT FULLY ACCESSIBLE ROUTE (FAR) SELECT 7 BONDS INDEX (INR)', 'NIFTY INDIA GOVERNMENT FULLY ACCESSIBLE ROUTE (FAR) SELECT 7 BONDS INDEX (USD)', 'NIFTY G-SEC JUN 2027 INDEX', 'NIFTY G-SEC DEC 2030 INDEX', 'NIFTY G-SEC DEC 2026 INDEX', 'NIFTY G-SEC JUL 2031 INDEX', 'NIFTY G-SEC SEP 2027 INDEX', 'NIFTY G-SEC JUN 2036 INDEX', 'NIFTY G-SEC SEP 2032 INDEX', 'NIFTY G-SEC DEC 2029 INDEX', 'NIFTY G-SEC OCT 2028 INDEX', 'NIFTY G-SEC APR 2029 INDEX', 'NIFTY G-SEC MAY 2029 INDEX', 'NIFTY INDIA SOVEREIGN GREEN BOND JAN 2033 INDEX', 'NIFTY INDIA SOVEREIGN GREEN BOND JAN 2028 INDEX', 'NIFTY G-SEC JUL 2027 INDEX', 'NIFTY G-SEC JUL 2033 INDEX']

    index = "NIFTY FMCG"
    index_data_path = f"data/indices/{index}_stocks.xlsx"

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
    losers.to_excel(f"data/indices/{index}_losers.xlsx", index=False)
    # Save gainers to a separate file
    gainers.to_excel(f"data/indices/{index}_gainers.xlsx", index=False)


if __name__ == "__main__":
    main()