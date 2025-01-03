# Finance Bot

## Currently available functions:

1. `alpha_finance.py`:  for getting all the relevant stock related information from well known Alpha Vantage API.
   1. Important Functions:
      1. `get_stock_price_data(ticker)`: for getting the price actions for a time period for a ticker
      2. `get_stock_financials`: for getting the financial for a ticker. This information can be used for FA later.
      3. `get_news_and_sentiment`: for getting the news and sentiment analysis of a ticker.
      4. `find_ticker`:finding the correct ticker symbol related to searched keywords.
2. `yahoo_finance.py`:  for getting all the relevant stock related information from well known Yahoo Finance API.
   1. Important Functions:
      1. `get_info`: for getting the info about a ticker or company.
      2. `get_history`: for getting the price actions for a time period for a ticker.
      3. `income_sheet_fa, balance_sheet_fa, cashflow_stmt_fa`: for getting the financial for a ticker. This information can be used for FA later.
      4. `get_recommendations`: getting the recommendations for a ticker.
3. `coffee_can_portfolio_screener.py`: To check if a particular company can be part of the [coffee can portfolio](https://groww.in/blog/the-coffee-can-portfolio).
   1. Instructions:
      1. invoke `coffee_can_eligible(ticker)` to get the results if the stock is eligible for a coffee can portfolio.
      2. Make sure you have the `income statement` and `balance sheet` for last at least last 10 Yrs saved locally for the stock. Feel free to play around the paths in the functions to read the data properly.
4. `news.py`: for getting latest news for the ticker or keyword. Perform sentiment analysis using NTP toolkits.
   1. Instructions:
      1. invoke `news_aggregator(ticker)` for getting all the latest news related to a ticker from teh sources listed below.
      2. invoke `senti_analysis(ticker)` for getting the sentiment analysis for the particular ticker.
   2. Supported sources: Google News, Yahoo News, NewsAPI news. More to come.
   3. Supported functions:
      1. `yahoo_news_screen(ticker)`: for getting the news from the `Yfinance API` for a ticker
      2. `google_news_screen(ticker)`: for getting the news from the `GNews API` for a ticker
      3. `newsapi_news_screen(ticker)`: for getting the news from the `NewsAPI API` for a ticker.
