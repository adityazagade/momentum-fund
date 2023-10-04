"""
This module contains NSEClient class which is a wrapper around nsepy library.
"""

import logging
import random
import time
from datetime import date
from typing import Any

import pandas as pd
import requests
from nsepy import get_history

from exceptions.nse_client_exceptions import NSEClientException
from model.company_info import CompanyInfo


class NSEClient:
    """
    This class is a wrapper around nsepy library. Since it has stopped working,
    we are directly fetching data from NSE website
    """
    instance = None

    def __init__(self) -> None:
        super().__init__()
        self.cookie = None
        self.logger = logging.getLogger(__name__)
        self.get_history = get_history
        self.nse_archives_base_url: str = "https://archives.nseindia.com"
        self.nse_base_url: str = "https://www.nseindia.com"
        self.cache = {}

    def get_data(self, symbol, start_date, end_date):
        """
        This method fetches historical data from NSE website. Currently,
        does not work as nsepy is not working
        :param symbol: stock symbol
        :param start_date: start date
        :param end_date: end date
        :return: historical data
        """
        data = self.get_history(symbol=symbol, start=start_date, end=end_date)
        return data

    def get_stock_universe(self, index: str):
        """
        This method fetches stock universe for a given index from NSE website
        :param index: index name (e.g. NIFTY 50)
        :return: list of stocks in the index
        """
        self.logger.info("Fetching stock universe for index: %s", index)
        url_template = "https://archives.nseindia.com/content/indices/ind_{index}list.csv"
        url = url_template.format(index=index.lower().replace(' ', ''))
        csv_df = pd.read_csv(url)
        return csv_df["Symbol"].tolist()

    def get_company_info(self, ticker: str) -> CompanyInfo:
        """
        This method fetches company info from NSE website if not already present in cache
        :param ticker: company ticker
        :return: company info
        """
        key = ticker + "_" + str(date.today())
        if key in self.cache:
            return self.cache[key]

        self.sleep_for_a_while()
        self.logger.info("Fetching company info for symbol: %s", ticker)
        url_template = self.nse_base_url + "/api" + f"/quote-equity?symbol={ticker}&section=trade_info"
        url = url_template.format(symbol=ticker)
        payload = {}
        headers = {
            'authority': 'www.nseindia.com',
            'accept': '*/*',
            'accept-language': 'en-GB,en;q=0.9',
            'cache-control': 'no-cache',
            'dnt': '1',
            'pragma': 'no-cache',
            'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        }
        response = requests.request("GET", url, headers=headers, data=payload, timeout=5, cookies=self.get_cookie())

        if response.status_code == 200:
            company_info = CompanyInfo.from_json(ticker, response.json())
            # update cache. key = symbol + date
            self.cache[key] = company_info
            return company_info
        message = f"Error fetching company info for symbol: {ticker}"
        raise NSEClientException(message)

    @staticmethod
    def sleep_for_a_while(min_seconds=1, max_seconds=4):
        """
        This method sleeps for a random number of seconds between min_seconds and max_seconds
        :return: None
        """
        random_number = random.randint(min_seconds, max_seconds)
        time.sleep(random_number)

    def get_cookie(self):
        """
        This method gets cookie from NSE website if not already present and returns it
        :return:
        """
        if not self.cookie:
            self.cookie = self.get_cookie_from_nse()
        return self.cookie

    def get_cookie_from_nse(self) -> dict[Any, Any]:
        """
        This method fetches cookie from NSE website
        :return: cookie dict
        """
        headers = {
            'accept': '*/*',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
            'accept-language': 'en,gu;q=0.9,hi;q=0.8',
            'accept-encoding': 'gzip, deflate, br',
        }
        session = requests.Session()
        dummy_response_to_get_cookies = session.get(self.nse_base_url, headers=headers, timeout=30)
        return dict(dummy_response_to_get_cookies.cookies)

    def try_to_get_company_info(self, ticker):
        """
        This method calls get_company_info method and retries if it fails max 3 times. Sleep for
        10 seconds between retries. Clear the cookie if it fails
        :param ticker: company ticker
        :return: company info
        """
        retry_count = 0
        while retry_count < 3:
            try:
                return self.get_company_info(ticker)
            except NSEClientException as ex:
                self.logger.error("Error fetching company info for symbol: %s", ticker)
                self.logger.error(ex)
                retry_count += 1
                self.cookie = None
                time.sleep(10)
        raise NSEClientException(f"Error fetching company info for symbol: {ticker}")

    @classmethod
    def get_instance(cls):
        """
        This method returns the singleton instance of NSEClient
        :return: NSEClient instance
        """
        if cls.instance is None:
            cls.instance = NSEClient()
        return cls.instance
