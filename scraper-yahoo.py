import os
import sys
import logging
import itertools
import json
import time
import urllib.request
from urllib.error import HTTPError
from datetime import datetime
from multiprocessing.dummy import Pool
from dependencies.LoggingCustomFormatter import LoggingCustomFormatter
from dependencies.common_funcs import check_www_conn, save_json, save_csv


# logger config
log = logging.getLogger("Yahoo scraper")
log.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(LoggingCustomFormatter())

log.addHandler(ch)


def get_historical_data(query_url, json_path, csv_path) -> None:
    stock_id = query_url.split("&period")[0].split("symbol=")[1]

    if os.path.exists(csv_path + stock_id + '.csv') and os.stat(csv_path + stock_id + '.csv').st_size != 0:
        log.info(f"Historical data of {stock_id} already exists")
        return

    while not check_www_conn():
        log.warning("Could not connect, trying again in 5 seconds...")
        time.sleep(5)

    try:
        with urllib.request.urlopen(query_url) as url:
            parsed_json = json.loads(url.read().decode())

    except HTTPError as e:
        if e.code == 429:
            log.error("HTTP Error 429: Too Many Requests")
        else:
            log.error(f"HTTP Error {e.code}")
    except Exception as e:
        print(e)
        log.warning("Historical data of " + stock_id + " cannot be found")
        return

    else:
        if os.path.exists(json_path + stock_id + '.json') and os.stat(json_path + stock_id + '.json').st_size != 0:
            os.remove(json_path + stock_id + '.json')

        save_json(parsed_json, json_path + stock_id + '.json')

        try:
            Date = []
            for i in parsed_json['chart']['result'][0]['timestamp']:
                Date.append(datetime.utcfromtimestamp(int(i)).strftime('%d-%m-%Y'))

            Low = parsed_json['chart']['result'][0]['indicators']['quote'][0]['low']
            Open = parsed_json['chart']['result'][0]['indicators']['quote'][0]['open']
            Volume = parsed_json['chart']['result'][0]['indicators']['quote'][0]['volume']
            High = parsed_json['chart']['result'][0]['indicators']['quote'][0]['high']
            Close = parsed_json['chart']['result'][0]['indicators']['quote'][0]['close']
            Adjusted_Close = parsed_json['chart']['result'][0]['indicators']['adjclose'][0]['adjclose']

            data = []
            for d, low, opn, vol, high, close, adj_close in zip(Date, Low, Open, Volume, High, Close, Adjusted_Close):
                data.append([d, low, opn, vol, high, close, adj_close])

            if os.path.exists(csv_path + stock_id + '.csv'):
                os.remove(csv_path + stock_id + '.csv')

            headers = ['Date', 'Low', 'Open', 'Volume', 'High', 'Close', 'Adjusted Close']
            save_csv(data, csv_path + stock_id + '.csv', headers)
            log.info(f"Historical data of {stock_id} save SUCCESS")
        except Exception as e:
            log.error(f"Retrieving historical data of {stock_id} FAIL: {str(e)}")

        return None


def main(tickers_csv_filepath: str, interval: str):
    json_output_path = f"{os.getcwd()}/output/stock_data/interval_{interval}/json/"
    csv_output_path = f"{os.getcwd()}/output/stock_data/interval_{interval}/csv/"

    if not os.path.isdir(json_output_path):
        os.makedirs(json_output_path)
    if not os.path.isdir(csv_output_path):
        os.makedirs(csv_output_path)

    query_urls = []
    with open(tickers_csv_filepath, 'r') as file:
        lines = file.readlines()
        for line in lines[1:]:  # Skip header
            ticker = line.strip().split(',')[0]  # Assuming 'ticker' is in first column
            query_urls.append(
                f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?symbol={ticker}&period1=0&period2=9999999999&interval={interval}&includePrePost=true&events=div%2Csplit")

    log.info(f"Total stocks to proceed: {len(query_urls)}")

    with Pool(processes=8) as pool:
        pool.starmap(get_historical_data, zip(query_urls, itertools.repeat(json_output_path), itertools.repeat(csv_output_path)))

    log.info("Stocks historical data successfully saved")
    return


if __name__ == '__main__':
    if len(sys.argv) > 1:
        stock_tickers_filepath = sys.argv[1]
        data_interval = sys.argv[2]
    else:
        stock_tickers_filepath = "./input/yahoo_stock_ticker_test_sample.csv"
        data_interval = "3mo"    # supported intervals: 3mo, 1d, 5m, 1m
    main(tickers_csv_filepath=stock_tickers_filepath, interval=data_interval)
