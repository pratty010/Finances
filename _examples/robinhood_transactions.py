import pandas as pd
import re

from collections import deque

from Finances._tools.file_operations import read_data, write_data
from Finances._tools.fin_funcs import convert_currency_to_float


def clean_data(file_path: str) -> tuple:
    """
    Cleans and filters financial transaction data to separate different types of transactions.

    This function takes a DataFrame containing financial transaction data and returns separate DataFrames
    for cash transactions, stock transactions, dividend transactions, fees transactions, and other transactions.

    Parameters:
    df (pd.DataFrame): A DataFrame containing financial transaction data with columns:"Activity Date", "Instrument", "Description", "Trans Code", "Quantity","Price", and "Amount".

    Returns:
    tuple: A tuple containing five elements:
        - df_cash (pd.DataFrame): A DataFrame containing only cash transactions.
        - df_stocks (pd.DataFrame): A DataFrame containing only stock transactions.
        - df_div (pd.DataFrame): A DataFrame containing only dividend transactions.
        - df_fees (pd.DataFrame): A DataFrame containing only fees transactions.
        - df_others (pd.DataFrame): A DataFrame containing all other transactions.

    Note:
    - The function filters the DataFrame based on specific transaction codes ('ACH', 'RTP', 'DCF', 'Buy', 'Sell', 'CDIV', 'AFEE', 'DFEE', 'DTAX').
    - The function also removes the filtered transactions from the original DataFrame to create 'df_others'.
    """

    # Read and clean the data
    df = read_data(file_path)

    # only keep the useful columns for processing.
    df = df[["Activity Date", "Instrument", "Description", "Trans Code", "Quantity", "Price(in $)", "Amount(in $)"]]

    # Filter the DataFrame to include only ACH and RTP transactions for deposits and withdrawals
    df_cash = df[(df['Trans Code'].isin(['ACH', 'RTP', 'DCF']))]

    # Filter out the stocks transactions for Buy and Sell
    df_stocks = df[df['Trans Code'].isin(['Buy', 'Sell'])]

    # Filter out the dividend received from the Holdings
    df_div = df[df['Trans Code'] == 'CDIV']

    # Filter out the fees and tax paid over time
    df_fees = df[df['Trans Code'].isin(['AFEE', 'DFEE', 'DTAX'])]

    # To remove the rest of the transactions
    indices_to_remove = pd.concat([pd.Series(df_cash.index),pd.Series(df_stocks.index), pd.Series(df_div.index),pd.Series(df_fees.index)]).unique()
    df_others = df.drop(indices_to_remove)

    return df_cash, df_stocks, df_div, df_fees, df_others

def process_options_transactions(df: pd.DataFrame) -> tuple:
    """
    Process and calculate the net total options traded from a given DataFrame.

    Parameters:
    df (pd.DataFrame): A DataFrame containing financial transaction data.

    Returns:
    tuple: A tuple containing two elements:
           - df_options (pd.DataFrame): A DataFrame containing only options transactions.
           - net_total (float): The net total options traded. The net total is calculated as the difference between the total options sold and total options bought.

    Note:
    - The function filters the DataFrame based on the 'BTO' transaction code.
    - The function calculates the total buy and sell amounts for calls and puts separately.
    - The function calculates the net total options traded as the difference between the total options sold
      and total options bought.
    """
    # Get transactions related to options traded
    df_options = df[df['Trans Code'] == 'BTO']

    # Calculate the total buy and sell amounts for calls and puts separately
    calls_bought = abs(df_options[(df_options['Amount'] < 0) & (df_options['Description'].str.contains(r'\bCall\b', case=False, na=False))]['Amount'].sum())
    calls_sold = df_options[(df_options['Amount'] > 0) & (df_options['Description'].str.contains(r'\bCall\b', case=False, na=False))]['Amount'].sum()
    puts_bought = abs(df_options[(df_options['Amount'] < 0) & (df_options['Description'].str.contains(r'\bPut\b', case=False, na=False))]['Amount'].sum())
    puts_sold = df_options[(df_options['Amount'] > 0) & (df_options['Description'].str.contains(r'\bPut\b', case=False, na=False))]['Amount'].sum()

    # Calculate the net total options traded
    total_bought = calls_bought + puts_bought
    total_sold = calls_sold + puts_sold
    net_total = total_sold - total_bought

    return df_options, net_total

def process_crypto_transactions(file_path: str) -> float:
    """
    Process and calculate the net investment from cryptocurrency transactions.

    This function reads and cleans the data from the specified file path, then calculates the total deposited and withdrawn amounts. It also calculates the net investment based on these amounts.

    Parameters:
    file_path (str): The path to the CSV file containing the cryptocurrency transaction data.The file should have columns 'Trans Code' and 'Amount(in $)'.

    Returns:
    float: The net investment from cryptocurrency transactions.
           The net investment is calculated as the difference between the total deposited and total withdrawn amounts.

    Note:
    The function prints the calculated net buy, net sold, and total investment values.
    """
    # Read and clean the data
    df_crypto = read_data(file_path)

    # Calculate the total deposited and withdrawn amount.
    # Calculate net investment based on it
    bought = df_crypto[df_crypto['Trans Code'] == 'Buy']['Amount(in $)'].sum()
    sold = df_crypto[df_crypto['Trans Code'] == 'Sell']['Amount(in $)'].sum()
    investment = bought - sold

    # Print the calculated values
    print('-' * 80)
    print(f"Net Buy > $ {bought}")
    print(f"Net Sold > $ {sold}")
    print(f"Total Investment > $ {investment}")
    print('-' * 80)

    # Calculate the total sent and received amount.
    # Calculate net sent or received from the it.
    sent = df_crypto[df_crypto['Trans Code'] == 'Sent']['Amount(in $)'].sum()
    received = df_crypto[df_crypto['Trans Code'] == 'Received']['Amount(in $)'].sum()
    net_sent = sent - received

    # Print the calculated values
    print('-' * 80)
    print(f"Total sent > $ {sent}")
    print(f"Total received > $ {received}")
    print(f"Net sent > $ {net_sent}")
    print('-' * 80)

    return investment

def calculate_weighted_avg_price(transaction_history: deque) -> tuple:
    """
    Calculates the weighted average price for a given transaction history.

    Parameters:
    transaction_history (deque): A deque containing tuples of the form (quantity, price), representing the transaction history.

    Returns:
    tuple: A tuple containing the weighted average price and a list of actualized P/L for each step in the transaction history.
    """
    # Variables to store the net total investment, total stocks held, average price and P/L.
    total_cost = 0.0
    total_qty = 0.0
    avg_price = 0.0
    actualized_pl = 0.0
    actualized_pl_list = []

    # Calculate the weighted average for the stocks held
    for qt, price in transaction_history:
        # Processing for the buy order.
        if qt > 0:
            # print(f"Processing buy order of {qt} @ $ {price}")
            total_qty += qt
            total_cost += (qt * price)
            # No change in P/L
        else:
            # If the quantity is negative, it means we're selling, so we need to adjust the cost and quantity.
            
            sell_qt = -qt # To simplify the calculation
            # print(f"Processing sell order of {sell_qt} @ $ {price}")

            actualized_pl +=  (price - avg_price) * sell_qt # P/L is calculated based on the selling price and current average price.
            total_cost -= (sell_qt * price)
            total_qty -= sell_qt

        # Calculate the average price if we have some holding of that stock
        avg_price = total_cost / total_qty if total_qty > 0 else 0
        # If total quantity is zero, we've sold all the stocks, so no further adjustments are needed.
        total_cost = total_cost if total_qty > 0 else 0

        # Store the actualized P/L for each step.
        actualized_pl_list.append(actualized_pl)

        # # Print the results at each step for inspection purposes
        # print(f"Total quantity : {total_qty}")
        # print(f"Total investment : {total_cost}")
        # print(f"Current Avg Price: $ {avg_price}")
        # print(f"Current Actualized P&L: $ {actualized_pl}")
        # print('-' * 80)

    return total_cost, avg_price, actualized_pl_list

def calculate_FIFO_avg_price(transaction_history: deque) -> tuple:
    """
    Calculates the weighted average price and actualized profit/loss for a given transaction history using the FIFO method.

    Parameters:
    transaction_history (deque): A deque containing tuples of the form (quantity, price), representing the transaction history.

    Returns:
    tuple: A tuple containing the weighted average price and a list of actualized P/L for each step in the transaction history.
    """
    avg_price = 0.0
    total_quantity = 0.0
    active_queue = deque()
    actualized_pl = 0.0
    actualized_pl_list = []
    total_inv = 0.0

    # Process the transaction history in FIFO manner.
    for qt, price in transaction_history:
        # Processing for the buy order.
        if qt > 0:
            print(f"Processing buy order of {qt} @ $ {price}")
            total_quantity += qt
            active_queue.append([qt, price])  # Append as a list
            avg_price = calculate_weighted_avg_price(active_queue)[1] # Calculate the weighted average for the current queue as it the actual avg price for this case.
        # Processing the sell order.
        else:
            print(f"Processing sell order of {qt} @ $ {price}")
            sell_qty = -qt  # Convert to positive for processing

            # Process the sell order while there are buy orders in the queue.
            while sell_qty > 0 and active_queue:
                old_qty, old_price = active_queue.popleft() # The leftmost order will be the order in question to fulfill the sell order
                if old_qty > sell_qty:
                    # Partially consume the buy order
                    active_queue.appendleft([old_qty - sell_qty, old_price]) # Update the leftmost order with updated left quantity after execution.
                    actualized_pl += (price - old_price) * sell_qty
                    total_quantity -= sell_qty
                    sell_qty = 0.0
                else:
                    # Fully consume the buy order
                    actualized_pl += (price - old_price) * old_qty
                    total_quantity -= old_qty
                    sell_qty -= old_qty

        # Recalculate average price if inventory remains
        results = calculate_weighted_avg_price(active_queue)

        # Store the actualized P/L for each step.
        actualized_pl_list.append(actualized_pl)

        # Print the results at each step for inspection purposes
        print(f"Total quantity : {total_quantity}")
        print(f"Total investment : {results[0]}")
        print(f"Current Avg Price: $ {results[1]}")
        print(f"Current Actualized P&L: $ {actualized_pl}")
        print('-' * 80)


    return results[0], results[1], actualized_pl_list

def calculate_avg_price(df: pd.DataFrame, stock: str, avg_type="FIFO") -> tuple:
    """
    Calculates the average price of a given stock based on the FIFO or weighted average method.

    Parameters:
    df (pd.DataFrame): The DataFrame containing the stock transaction data.
    stock (str): The symbol of the stock for which the average price needs to be calculated.
    avg_type (str): The method to calculate the average price. It can be either "FIFO" or "Weighted". Default is "FIFO".

    Returns:
    tuple: A tuple containing the net average price and the actualized profit/loss for each step in the transaction history.
    """

    # Extract the data for a given stock
    # Convert the quantity to float
    df_orders = df[df['Instrument'] == stock]
    df_orders['Quantity'] = df_orders['Quantity'].astype(float)
    # print(df_orders.head(15))

    # Invert the DataFrame (for ascending order of transactions).
    inverted_df = df_orders.sort_index(ascending=False)
    useful_data = inverted_df[['Activity Date', 'Trans Code', 'Quantity', 'Price(in $)']]
    # print(useful_data.head(15))
    
    # to store stocks transactions in a ordered queue
    transaction_history = []

    # Run through all the values for storing and selling transactions from a queue
    for row in useful_data.itertuples(index=False):
        # print(row)

        act_date = row[0]
        action = row[1]
        qt = row[2]
        price = row[3]
        
        if action == 'Buy':
            transaction_history.append([qt, price])
            # print(f"Bought {qt} stocks at $ {price} on {act_date}")
            # print('--' * 80)
        elif action == 'Sell':
            transaction_history.append([- qt, price])
            # print(f"Sold {qt} stocks at $ {price} on {act_date}")
            # print('--' * 80)

    # Calculate the average price using the selected method
    if avg_type == "FIFO":
        total_inv, avg_price, pl = calculate_FIFO_avg_price(transaction_history)
    elif avg_type == "Weighted":
        total_inv, avg_price, pl = calculate_weighted_avg_price(transaction_history)
    else:
        print("Invalid average type. Please choose either FIFO or Weighted.")


    print(f"Total Net Investment > $ {total_inv}")
    print(f"Net Average Price > $ {avg_price}")
    print(f"Actualized Profit/Loss > $ {pl[-1]}")

    return total_inv, avg_price, pl

def process_cash_transactions(df_cash: pd.DataFrame, df_others: pd.DataFrame, crypto: float) -> None:
    """
    Processes cash transactions data to calculate net cash deposited, considering deposits, withdrawals,
    crypto investments, and options trading.

    Parameters:
    df_cash (pd.DataFrame): A DataFrame containing cash transaction data. It should have columns 'Amount'.
    df_others (pd.DataFrame): A DataFrame containing all other transaction data.
    crypto (float): The total amount invested in cryptocurrencies.

    Returns:
    None: The function prints the calculated values for total deposits, total withdrawals, crypto investment, options trading, net cash deposited, current invested, and charges and tax.
    """
    # Calculate the total deposits and total withdrawals
    deposits = df_cash[df_cash['Amount'] > 0]['Amount'].sum()
    withdrawals = abs(df_cash[df_cash['Amount'] < 0]['Amount'].sum())
    options = process_options_transactions (df_others)[1]

    # Calculate the net cash deposited
    cash = deposits - withdrawals - crypto - options
    current_invested = 0.0 # Edit with current investment or use the avg price functions to get the total investment
    charges = cash - current_invested

    # Print the calculated values
    print('-' * 80)
    print(f"Total deposits > $ {deposits}")
    print(f"Total withdrawals > $ {withdrawals}")
    print('-' * 80)
    print(f"Crypto investment > $ {crypto}")
    print('-' * 80)
    print(f"Options trading > $ {options}")
    print('-' * 80)
    print(f"Net cash Deposited > $ {cash}")
    print(f"Current Invested > $ {current_invested}")
    print(f"Charges and Tax > $ {charges}")
    print('-' * 80)

    
def main():
    
    fd_records = "_data/personal_statements/Robinhood_Records.csv"
    fd_crypto = "_data/personal_statements/Robinhood_Crypto.csv"

    # df = read_data(fd_records, sheet_name="6b6958e8-d4e2-53fe-a806-201ff55")
    # write_data("_data/personal_statements/Robinhood_Records.csv", df)
    # print(df.info())

    # # calculate investment from crypto transactions
    # crypto = process_crypto_transactions(fd_crypto)
    # print(f"Total Crypto Investment > $ {crypto}")

    # Clean the statement to get various datasets
    df_cash, df_stocks, df_div, df_fees, df_others = clean_data(fd_records)

    # # # check out the options transactions data
    # # _,options = process_options_transactions(df_others)
    # # print(f"Total Options Investment > $ {options}")
    
    # Get list of all traded stocks
    stocks = df_stocks['Instrument'].unique()
    print(stocks)
    print("-" * 80)

    # Calculate investment for QCOM stock
    transc_history = calculate_avg_price(df_stocks, 'QCOM')


    # To do it for all the traded stocks.
    inv = 0.0
    pl = 0.0
    for stock in stocks:
        print(f"processing for stock - {stock}")
        transc_history = calculate_avg_price(df_stocks, stock)
        # print(f"Net Investment of {stock} > ${transc_history[0]}")
        inv += transc_history[0]
        pl += transc_history[2][-1]  # considering only the last P/L value as it represents the current P/L.
        print('--' * 80)
        
    print(f"Net Total Investment > ${inv}")
    print(f"Net Total Actualized P/L > ${pl}")

    
if __name__ == '__main__':
    main()