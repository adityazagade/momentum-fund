import time
from abc import ABC, abstractmethod

import pandas as pd
import requests
from kiteconnect import KiteConnect
from pandas import DataFrame

from config.app_config import AppConfig
from model.Ohlcv import OhlcData


class KiteClient(ABC):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def get_data(self, symbol, start_date, end_date, interval="day") -> OhlcData:
        pass


class HttpKiteClient(KiteClient):
    def __init__(self) -> None:
        super().__init__()
        app_config = AppConfig('app.properties')
        self.base_url = app_config.get('kite.ui.base_url')
        self.session = app_config.get('kite.ui.cookies.session')
        self.csrf_token = app_config.get('kite.ui.csrf_token')
        self.client_id = app_config.get('kite.ui.client_id')
        self.public_token = app_config.get('kite.ui.public_token')
        # load instrments.csv into a dataframe
        self.instruments_df = pd.read_csv('instruments.csv')

    def get_data(self, symbol, start_date, end_date, interval="day") -> OhlcData:
        # sleep for 1 second to avoid rate limit
        time.sleep(1)
        url_template = "{base_url}/oms/instruments/historical/{instrument_token}/day?user_id={client_id}&oi={oi}&from={start_date}&to={end_date}"
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        instrument_token = self.get_instrument_token(symbol)
        url = url_template.format(
            base_url=self.base_url,
            instrument_token=instrument_token,
            client_id=self.client_id,
            start_date=start_date_str,
            end_date=end_date_str,
            oi=0)
        headers = self.get_headers()
        payload = {}
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        return OhlcData.from_json(data)

    def get_instrument_token(self, ticker, exchange="NSE"):
        tradingsymbol_ticker_filter = self.instruments_df['tradingsymbol'] == ticker
        instrument_token = self.instruments_df.loc[tradingsymbol_ticker_filter]['instrument_token'].values[0]
        return instrument_token

    def get_headers(self):
        cookie = str(f'user_id={self.client_id}; public_token={self.public_token}; kf_session={self.session}')
        headers = {
            'authority': 'kite.zerodha.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'authorization': 'enctoken ivOjK/rzFJMwWBlahBKbB8nDmUCAfGMIwsIKGAWzEfTrg6ACRoUekxwnoL5RyrA08XR30FcqSSuGgMopSHwVoimo3a5ac1JRaX+00va54+2CnAGOInGYvQ==',
            # 'cookie': 'intercom-id-y72tx0ov=6aad72ce-4c70-42df-8301-5f99edc2052a; intercom-device-id-y72tx0ov=4db3b5c7-bbd6-4024-aed1-c1f03a35e78a; AMP_MKTG_d9d4ec74fa=JTdCJTIycmVmZXJyZXIlMjIlM0ElMjJodHRwcyUzQSUyRiUyRnN0b2Nrcy50aWNrZXJ0YXBlLmluJTJGJTIyJTJDJTIycmVmZXJyaW5nX2RvbWFpbiUyMiUzQSUyMnN0b2Nrcy50aWNrZXJ0YXBlLmluJTIyJTdE; AMP_d9d4ec74fa=JTdCJTIyZGV2aWNlSWQlMjIlM0ElMjJmMjg4MDY3ZS1jMTVlLTQ3NDgtOWEyOS0xNTY0ZTBhYjY1N2QlMjIlMkMlMjJzZXNzaW9uSWQlMjIlM0ExNjkxNDg3NzY0OTUzJTJDJTIyb3B0T3V0JTIyJTNBZmFsc2UlMkMlMjJsYXN0RXZlbnRUaW1lJTIyJTNBMTY5MTQ4Nzc3OTg1NiUyQyUyMmxhc3RFdmVudElkJTIyJTNBNSU3RA==; intercom-id-tp6yd2q1=d241d1b4-693b-450a-a2ef-7b749fddfcf8; intercom-device-id-tp6yd2q1=a390f9a3-efbf-4f93-a2cb-97ae1ed4f946; _cfuvid=7OKsm9lFAuL91oBmYPAnOVEhY_UwQj8Zh7Dw5UkKELQ-1694448435817-0-604800000; kf_session=yooSc9DmTNWN8TMoaJpTSKekos64E9h7; user_id=KW3437; public_token=KpUAgJMI7iOUUIFFQtxYLyP1bJOVXS09; enctoken=ivOjK/rzFJMwWBlahBKbB8nDmUCAfGMIwsIKGAWzEfTrg6ACRoUekxwnoL5RyrA08XR30FcqSSuGgMopSHwVoimo3a5ac1JRaX+00va54+2CnAGOInGYvQ==',
            'dnt': '1',
            'referer': 'https://kite.zerodha.com/chart/web/tvc/NSE/DIXON/5552641',
            'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
            # 'x-kite-userid': self.client_id,
            # 'x-csrftoken': self.csrf_token,
            # 'cookie': cookie
        }
        return headers


class KiteSDKClient(KiteClient):
    def __init__(self) -> None:
        super().__init__()
        self.app_config = AppConfig('app.properties')
        api_key = self.app_config.get('kite.api_key')
        api_secret = self.app_config.get('kite.api_secret')
        request_token = self.app_config.get('kite.request_token')
        access_token = self.app_config.get('kite.access_token')
        public_token = self.app_config.get('kite.public_token')
        kite = KiteConnect(api_key=api_key)

        if request_token is None or request_token == '':
            url = kite.login_url()
            print(url)

        if is_null_or_empty(access_token) or is_null_or_empty(public_token):
            data = kite.generate_session(request_token=request_token, api_secret=api_secret)
            public_token_ = data["public_token"]
            access_token_ = data["access_token"]
            access_token = access_token_
            public_token = public_token_
            self.update_config_in_file(access_token_, public_token_)

        kite.set_access_token(access_token)
        self.kite = kite

        instruments_df = self.get_instruments()
        # save instruments_df
        # instruments_df.to_csv('instruments.csv', index=False)
        nifty200_constituents_df = pd.read_csv('ind_nifty200list.csv')
        tokens_df = pd.merge(nifty200_constituents_df, instruments_df[['instrument_token', 'tradingsymbol']],
                             how='left',
                             left_on=['Symbol'], right_on=['tradingsymbol'])
        # tokens_df.instrument_token = tokens_df.instrument_token.astype('int')
        # tokens_df = tokens_df[~tokens_df['instrument_token'].isna()].copy()
        self.tokens_df = tokens_df
        self.instruments_df = instruments_df

    def get_data(self, symbol, start_date, end_date, interval="day") -> OhlcData:
        print("Fetching data for symbol: " + symbol)
        df = self.instruments_df
        filtered_row = df[df['tradingsymbol'] == symbol]
        instrument_token = int(filtered_row['instrument_token'].iloc[0])
        response = self.kite.historical_data(
            instrument_token=instrument_token,
            from_date=start_date,
            to_date=end_date,
            interval=interval
        )
        return OhlcData.from_kite_trade_api_response(response)

    def get_instrument_token(self, ticker, exchange="NSE"):
        response = self.kite.instruments(exchange=exchange)
        for instrument in response:
            if instrument['tradingsymbol'] == ticker:
                return instrument['instrument_token']
        return None

    def get_instruments(self, exchange="NSE"):
        response = self.kite.instruments(exchange=exchange)
        return DataFrame(response)

    def update_config_in_file(self, access_token_, public_token_):
        self.app_config.set('kite.access_token', access_token_)
        self.app_config.set('kite.public_token', public_token_)
        self.app_config.write()


def is_null_or_empty(text):
    return text is None or text == ''
