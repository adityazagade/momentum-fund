from kiteconnect import KiteConnect
from pandas import DataFrame
from config.app_config import AppConfig
import pandas as pd


def is_null_or_empty(text):
    return text is None or text == ''


class KiteConnectService:
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
        nifty200_constituents_df = pd.read_csv('ind_nifty200list.csv')
        tokens_df = pd.merge(nifty200_constituents_df, instruments_df[['instrument_token', 'tradingsymbol']],
                             how='left',
                             left_on=['Symbol'], right_on=['tradingsymbol'])
        # tokens_df.instrument_token = tokens_df.instrument_token.astype('int')
        # tokens_df = tokens_df[~tokens_df['instrument_token'].isna()].copy()
        self.tokens_df = tokens_df
        self.instruments_df = instruments_df

    def get_data(self, symbol, start_date, end_date, interval="day") -> DataFrame:
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
        return DataFrame(response)

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
