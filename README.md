# financial-data-web-scraper

### Example usage
```shell
python yahoo-scrapper.py ./yahoo_stock_ticker_test_sample.csv 1d
```

### Available intervals:

- &interval=3mo - 3 months, going back until initial trading date.
- &interval=1d  - 1 day, going back until initial trading date.
- &interval=5m  - 5 minutes, going back 80(ish) days.
- &interval=1m  - 1 minute, going back 4-5 days.