import os
import pandas as pd

def create_folder(folder_name: str):
    """
    Creates a new folder with the provided name. If the folder already exists, the function does nothing.

    Args:
    folder_name (str): The name of the folder to be created. It should be a string.

    Returns:
    None: The function does not return any value.
    """
    # Check if the folder already exists
    if not os.path.exists(folder_name):
        # If the folder does not exist, create it
        os.makedirs(folder_name)
        # Print a success message
        print(f"Folder '{folder_name}' created successfully.")
        print("-" * 80)
    else:
        # If the folder already exists, print a message and move on
        print(f"Folder '{folder_name}' already exists. Moving on...")
        print("-" * 80)

def read_data(file_path: str, index: str = None) -> pd.DataFrame:
    """
    This function reads data from a local CSV or Excel file and returns it as a pandas DataFrame.
    If the file does not exist locally, it prints a message and returns an empty DataFrame.
    If the file exists but is empty, it also prints a message and returns an empty DataFrame.
    If the file format is not supported (i.e., not CSV or Excel), it prints an error message and returns an empty DataFrame.

    Parameters:
    file_path (str): The path to the local CSV or Excel file. This parameter is required and must be a string.
    index (str): The column name to use as the index for the DataFrame. This parameter is optional and defaults to "Date".

    Returns:
    pd.DataFrame: The data read from the file as a pandas DataFrame. If the file does not exist, is empty, or has an unsupported format, an empty DataFrame is returned.
    """
    # Create the directory if it doesn't exist
    folder_path = os.path.dirname(file_path)
    create_folder(folder_path)

    # Check if the file already exists locally
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        if ".csv" in file_path:
            print(f"Loading the data from the CSV file: {file_path}")
            print("-" * 80)
            df = pd.read_csv(file_path, index_col=index)  # Read CSV file into DataFrame
        elif ".xlsx" in file_path:
            print(f"Loading the data from the Excel file: {file_path}")
            print("-" * 80)
            df = pd.read_excel(file_path, index_col=index)  # Read Excel file into DataFrame
        else:
            print(f"Unsupported file format: {file_path}. Please use either a CSV or Excel file.")
            print("-" * 80)
            return pd.DataFrame()  # Return empty DataFrame for unsupported file format

        return df  # Return the DataFrame
    else:
        print(f"File '{file_path}' does not exist locally. Moving ahead....")
        print("-" * 80)
        return pd.DataFrame()  # Return empty DataFrame for non-existent or empty file

def write_data(file_path: str, df: pd.DataFrame):
    """
    Writes historical stock price data to a CSV or Excel file. If the file does not exist,
    it creates a new file. If the file exists, it updates the existing file with the new data.

    Parameters:
    file_path (str): The name of the CSV or Excel file where the historical stock price data will be saved.
    df (pd.DataFrame): A pandas DataFrame containing the historical stock price data.

    Returns:
    None. The function writes the data to the file and prints appropriate messages.
    """

    # If the file path is empty, print an error message and return
    if file_path is None:
        print("No file path provided. Moving ahead with retrieval...")
        print("-" * 80)
        return

    else:
        print("Writing data to the file...")
        print("-" * 80)
        
        # Determine the file format based on the file extension
        if ".csv" in file_path:
            print(f"Writing updated data to the CSV file: {file_path}")
            df.to_csv(file_path, index="Date")  # Write DataFrame to CSV file
        elif ".xlsx" in file_path:
            print(f"Writing updated data to the Excel file: {file_path}")
            df.to_excel(file_path, index="Date")  # Write DataFrame to Excel file
        else:
            print(f"Unsupported file format: {file_path}. Please use either a CSV or Excel file.")
        print("-" * 80)
        
def main():

    # Example usage
    read_path = "fin_bot/data/tabula-Transactions_Holdings_Statement_revised.xlsx"
    write_path = "fin_bot/data/tabula-Transactions_Holdings_Statement_revised.csv"

    df = read_data(read_path)
    write_data(write_path, df)


if __name__ == "__main__":
    main()