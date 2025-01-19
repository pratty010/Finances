# Finance Bot

## Currently available functions:

1. `robinhood_transactions.py`: For making it easier to have a look into your Robinhood transaction statements.

   1. `clean_data(file_path)`: To clean up the data and get the various datasets based on the transactions type.
   2. `process_crypto_transactions(file_path)`: To get all the useful crypto transactions and the associated functions with it.
   3. `process_cash_transactions(df_cash, df_others, crypto)` : Uses the cash and other transactions to get you an outlook of your current investment stage.
   4. `calculate_avg_price(df, stock, avg_type="FIFO")`: To get you the total investment, average price and total P/L based on the avg method chosen. Can be either "FIFO" or "Weighted". Can plug the total investment in process_cash_transactions().
      Note: Still in works for the splitting adjustment.
2. `alpha_finance.py`:  for getting all the relevant stock related information from well known Alpha Vantage API.

   1. Important Functions:
      1. `get_stock_price_data(ticker)`: for getting the price actions for a time period for a ticker
      2. `get_stock_financials`: for getting the financial for a ticker. This information can be used for FA later.
      3. `get_news_and_sentiment`: for getting the news and sentiment analysis of a ticker.
      4. `find_ticker`:finding the correct ticker symbol related to searched keywords.
3. `yahoo_finance.py`:  for getting all the relevant stock related information from well known Yahoo Finance API.

   1. Important Functions:
      1. `get_info`: for getting the info about a ticker or company.
      2. `get_history`: for getting the price actions for a time period for a ticker.
      3. `income_sheet_fa, balance_sheet_fa, cashflow_stmt_fa`: for getting the financial for a ticker. This information can be used for FA later.
      4. `get_recommendations`: getting the recommendations for a ticker.
4. `coffee_can_portfolio_screener.py`: To check if a particular company can be part of the [coffee can portfolio](https://groww.in/blog/the-coffee-can-portfolio).

   1. Instructions:
      1. invoke `coffee_can_eligible(ticker)` to get the results if the stock is eligible for a coffee can portfolio.
      2. Make sure you have the `income statement` and `balance sheet` for last at least last 10 Yrs saved locally for the stock. Feel free to play around the paths in the functions to read the data properly.

## Under Work functions:

1. `news.py`: for getting latest news for the ticker or keyword. Perform sentiment analysis using NTP toolkits.
   1. Instructions:
      1. invoke `news_aggregator(ticker)` for getting all the latest news related to a ticker from teh sources listed below.
      2. invoke `senti_analysis(ticker)` for getting the sentiment analysis for the particular ticker.
   2. Supported sources: Google News, Yahoo News, NewsAPI news. More to come.
   3. Supported functions:
      1. `yahoo_news_screen(ticker)`: for getting the news from the `Yfinance API` for a ticker
      2. `google_news_screen(ticker)`: for getting the news from the `GNews API` for a ticker
      3. `newsapi_news_screen(ticker)`: for getting the news from the `NewsAPI API` for a ticker.
2. `ind_index.py`
3. `groww_transcations.py`
4. `coingecko.py`
