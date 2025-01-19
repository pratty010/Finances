import os
import pandas as pd

def create_folder(file_path: str):
    """
    Creates a folder for the given file path if it doesn't already exist.

    This function extracts the directory path from the given file path and creates
    the folder if it doesn't exist. If the folder already exists, it prints a message
    indicating so.

    Parameters:
    file_path (str): The full path of the file for which the folder needs to be created.

    Returns:
    None

    Prints:
    - A message indicating whether the folder was created or already existed.
    - A separator line for visual clarity in the output.
    """
    # Extract the directory path
    dir_path = os.path.dirname(file_path)

    # Check if the folder already exists
    if os.path.exists(dir_path) and os.path.isdir(dir_path):
        # If the folder already exists, print a message and move on
        print(f"* Folder '{dir_path}' already exists. Moving on...")
        print("-" * 80)
    # If the folder does not exist, create it
    else:
        os.makedirs(dir_path)
        # Print a success message
        print(f"* Folder '{dir_path}' created successfully.")
        print("-" * 80)
        
def read_data(file_path: str, index: str = None, sheet_name: list = None) -> pd.DataFrame:
    """
    Reads data from a CSV or Excel file into a pandas DataFrame.

    This function takes a file path, an optional index column, and an optional list of sheet names.
    It checks if the file path is valid, whether the file exists locally, and whether the file format is supported.
    If the file is valid and exists, it reads the data into a pandas DataFrame.

    Parameters:
    file_path (str): The path to the CSV or Excel file to be read.
    index (str, optional): The column name to use as the index in the DataFrame. Defaults to None.
    sheet_name (list, optional): A list of sheet names to read from the Excel file. Defaults to None.

    Returns:
    pd.DataFrame: A pandas DataFrame containing the data from the file. If the file path is invalid, the file does not exist, or the file format is unsupported, an empty DataFrame is returned.

    Prints:
    - Informative messages about the reading process or any issues encountered.
    - A separator line for visual clarity in the output.
    """
    # Check if the supplied path is not None
    if not file_path:
        print("! The file path is None. Please provide a valid file path.")
        print("-" * 80)
        return pd.DataFrame()  # Return empty DataFrame for None file path
    # Check if the file already exists locally
    elif os.path.exists(file_path) and os.path.isfile(file_path) and os.path.getsize(file_path) > 0:
        if ".csv" in file_path:
            print(f"< Loading the data from the CSV file: {file_path}")
            print("-" * 80)
            df = pd.read_csv(file_path, index_col=index)  # Read CSV file into DataFrame
        elif ".xlsx" in file_path:
            print(f"< Loading the data from the Excel file: {file_path}")
            print("-" * 80)
            df = pd.read_excel(file_path, index_col=index, sheet_name=sheet_name)  # Read Excel file into DataFrame
        else:
            print(f"! Unsupported file format: {file_path}. Please use either a CSV or Excel file.")
            print("-" * 80)
            return pd.DataFrame()  # Return empty DataFrame for unsupported file format
        return df  # Return the DataFrame
    else:
        print(f"! File '{file_path}' does not exist locally. Moving ahead....")
        print("-" * 80)
        return pd.DataFrame()  # Return empty DataFrame for non-existent or empty file

def write_data(file_path: str, df: pd.DataFrame):
    """
    Writes a pandas DataFrame to a CSV or Excel file.

    This function takes a file path and a pandas DataFrame, and writes the DataFrame
    to the specified file. It handles the creation of the directory if it doesn't exist,
    and supports writing to both CSV and Excel formats.

    Parameters:
    file_path (str): The path where the file should be written. Should end with '.csv' or '.xlsx'.
    df (pd.DataFrame): The pandas DataFrame containing the data to be written.

    Returns:
    None

    Prints:
    - Informative messages about the writing process or any issues encountered.
    - A separator line for visual clarity in the output.
    """

    # Check if the supplied path is not None
    if not file_path:
        print("! The file path is None. Please provide a valid file path.")
        print("-" * 80)
    else:

        # Create the directory if it doesn't exist
        create_folder(file_path)

        # Determine the file format based on the file extension
        if ".csv" in file_path:
            print(f"> Writing updated data to the supplied CSV file: {file_path}")
            df.to_csv(file_path, index=False)  # Write DataFrame to CSV file
        elif ".xlsx" in file_path:
            print(f"> Writing updated data to the supplied Excel file: {file_path}")
            df.to_excel(file_path, index=False)  # Write DataFrame to Excel file
        else:
            print(f"! Unsupported file format: {file_path}. Please use either a CSV or Excel file.")
        print("-" * 80)
        
def main():

    # Example usage
    read_path = "data/crypto/BTC/prices/historical.csv"
    write_path = "data/crypto/BTC/prices/historical.xlsx"

    df = read_data(read_path)
    # print(df.head(20))

    # write_data(write_path, df)


if __name__ == "__main__":
    main()