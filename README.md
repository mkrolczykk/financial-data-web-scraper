# financial-data-web-scraper

Project for the subject Automata, Languages, Calculations (AJO)

### Example usage
```shell
python scraper-yahoo.py ./input/yahoo_stock_ticker_test_sample.csv 1d
```

```shell
python scraper-etherscan.py ./input/etherscan_transactions.csv
```

### Yahoo scraper available intervals:

- &interval=3mo - 3 months (data range from initial trading date)
- &interval=1d  - 1 day (data range from initial trading date)
- &interval=5m  - 5 minutes (data range ~ 80 days)
- &interval=1m  - 1 minute (data range 4-5 days)