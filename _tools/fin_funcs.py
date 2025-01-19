import pandas as pd
import yfinance as yf


def convert_currency_to_float(amount: str) -> float:
    """
    Convert a string representing a currency amount to a float.

    This function takes a string representing a currency amount and returns the equivalent float value.
    It handles currency formatting, including removing commas and dollar signs, and handling negative values in parentheses.

    Parameters:
    amount (str): A string representing a currency amount. It can include commas, dollar signs, and negative values in parentheses.

    Returns:
    float: The equivalent float value of the currency amount. If the input string cannot be converted to a float, the function returns None.
    """
    # Check if the value is NaN and return None if true
    if pd.isna(amount):  
        return None

    # Process the value assuming it's a string with currency formatting
    try:
        # Remove commas and dollar signs
        amount = amount.replace(',', '').replace('$', '')

        # Check for negative values in parentheses
        if '(' in amount and ')' in amount:
            return -float(re.sub(r'[()]', '', amount))
        else:
            return float(amount)
    except ValueError:
        return None  # Return None for unexpected formats
    
    
def get_ticker_isin(ISIN: str = None, country: str = 'india') -> str:
    """
    Retrieves the stock ticker symbol for a given International Securities Identification Number (ISIN)
    using Yahoo Finance and Yahoo Query Library.

    This function first attempts to find the ticker using Yahoo Finance. If unsuccessful, it then tries
    the Yahoo Query Library. If no ticker is found using either method, it returns None.

    Parameters:
    ISIN (str): The International Securities Identification Number for which the ticker symbol needs to be found.
    country (str): The country in which the stock is listed. Default is 'india'.

    Returns:
    str or None: The stock ticker symbol corresponding to the given ISIN if found, None otherwise.

    Raises:
    Exception: If an error occurs during the process of retrieving the ticker symbol.
    """

    try:
        print(f"Trying to find ticker for {ISIN} using Yahoo Finance.....")
        # Use Yahoo Finance to find the ticker using ISIN provided
        ticker  = yf.utils.get_ticker_by_isin(ISIN)
        # To check if the api call returns valid result (any result)
        if len(ticker) == 0 or ticker is None:
            print(f"No ticker found for ISIN: `{ISIN}` using Yahoo Finance.")
            try:
                # If not invoking the yahoo query api request to dig further.
                print("Trying the Yahoo query library......")
                res = yq.search(ISIN, country) # Search for ISIN as keyword in mentioned country.
                ticker = res['quotes'][0]['symbol'] if res['quotes'] else None
                if ticker is None:
                    print(f"No ticker found for ISIN: `{ISIN}` using Yahoo query library. Returning None as the ticker.")
                    return None
                else:
                    print(f"Ticker found using Yahoo query library: {ticker}")
            except Exception as e:
                print(f"Error occurred while trying Yahoo query library: {e}")
        else:
            print(f"Ticker found using Yahoo Finance: {ticker}")

        return ticker


    except:
        print(f"Error occured for '{ISIN}'")
        return None

def process_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    This function processes a DataFrame containing historical stock price data. It performs the following tasks:
    1. Renames the columns to a standard format.
    2. Converts the 'Date' column to datetime type and sets it as the index.
    3. Converts the 'Open', 'High', 'Low', 'Close' columns to dtype float.
    4. Converts the 'Volume' column to dtype int and divides by 1,000,000 to get the volume in millions.
    5. Calculates the net change in price.
    6. Rounds the 'Open', 'High', 'Low', 'Close', and 'Net Change' columns to two decimal places.
    7. Rounds the 'Volume' column to three decimal places.
    8. Sorts the DataFrame in descending order based on the 'Date' index.

    Parameters:
    df (pd.DataFrame): The DataFrame containing historical stock price data.
    source (str): The source of the data ('alpha' or 'yf').

    Returns:
    pd.DataFrame: The processed DataFrame containing the historical stock price data.
    tuple: A tuple containing the minimum and maximum dates in the processed DataFrame.
    """
    # # Test out the initial DataFrame
    # print(df.info())
    # print(df.head())

    # Convert the 'Open', 'High', 'Low', 'Close' columns to dtype float and round to two decimal
    df[['Open', 'High', 'Low', 'Close']] = df[['Open', 'High', 'Low', 'Close']].astype(float).round(2)
    
    # Convert the 'Volume' column to dtype int and divide by 1,000,000 to get million
    df['Volume'] = df['Volume'].astype(int) / 1000000
    df['Volume'] = df['Volume'].round(3) # Round the volume to three decimal places

    df['Net Change'] = (df['Close'] - df['Open'])/df['Open'] * 100  # Calculate the net change
    df['Net Change'] = df['Net Change'].round(2) # Round the net change to 2 decimal places
    
    # print(df.head())
    return df

def main():
    # Define the keyword and country for the stock ticker search
    keyword = "INE423A01024"
    country = "India"

    # Get the stock ticker symbol using the Yahoo Query Language (YQL)
    ticker_sybl = get_ticker_isin(keyword, country)
    print(ticker_sybl)

    

if __name__ == "__main__":
    main()