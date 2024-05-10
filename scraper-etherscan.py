import os
import sys
import time
import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dependencies.regex_lib import match
from dependencies.LoggingCustomFormatter import LoggingCustomFormatter
from dependencies.common_funcs import check_www_conn, save_csv


# logger config
log = logging.getLogger("Etherscan.io scraper")
log.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(LoggingCustomFormatter())

log.addHandler(ch)


def get_transaction_summary(transaction_hash):
    url = f"https://etherscan.io/tx/{transaction_hash}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

    while not check_www_conn():
        log.warning("Could not connect, trying again in 5 seconds...")
        time.sleep(5)

    response = requests.get(url, headers=headers)

    soup = BeautifulSoup(response.content, 'html.parser')

    found_divs = []
    for div in soup.find_all('div'):
        spans = div.find_all('span', recursive=False)
        if len(spans) >= 8:
            found_divs.append(div)

    result = []
    if found_divs:
        for div in found_divs:
            spans = div.find_all('span', recursive=False)
            for span in spans:
                result.append(span.get_text())
        return result
    else:
        log.error(f"Parsing ERROR: Couldn't retrieve Transaction Action Summary data for transaction ID: {transaction_hash}")
        return []


def _save_to_csv(data, csv_output_path, filename="result"):
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d-%H-%M-%S")
    filename = f"{filename}_{timestamp}.csv"

    headers = ['Transaction Hash', 'Transaction Action Summary']
    save_csv(data, f"{csv_output_path}/{filename}", headers)


def main(transactions_filepath: str):
    csv_output_path = f"{os.getcwd()}/output/etherscan_data/csv"

    if not os.path.isdir(csv_output_path):
        os.makedirs(csv_output_path)

    transactions_ids = []
    with open(transactions_filepath, 'r') as file:
        lines = file.readlines()
        log.info(f"Total transactions to proceed: {len(lines) - 1}")
        for line in lines[1:]:  # Skip header
            regex_expr = '^https://(\\a|\\d)+.(com|net|org|io)'
            if match(regex_expr, line.strip().split(',')[0])[0]:    # if event src match regex expr
                transactions_ids.append(line.strip().split(',')[2])
            else:
                pass

    result = []
    for trx_hash in transactions_ids:
        result.append([trx_hash, get_transaction_summary(trx_hash)])

    _save_to_csv(result, csv_output_path)
    log.info("Etherscan transactions data successfully saved")
    return


if __name__ == '__main__':
    if len(sys.argv) > 1:
        input_filepath = sys.argv[1]
    else:
        input_filepath = "./input/etherscan_transactions.csv"

    main(transactions_filepath=input_filepath)
