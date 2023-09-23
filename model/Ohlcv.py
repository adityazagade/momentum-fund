from datetime import datetime

from pandas import DataFrame
from typing import List

import constants.column_names as column_names


class Ohlcv:
    def __init__(self, open_price, high, low, close, volume, date_time: datetime) -> None:
        super().__init__()
        self.open = open_price
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.date_time = date_time

    def __str__(self) -> str:
        return f"Open: {self.open}, High: {self.high}, Low: {self.low}, Close: {self.close}, Volume: {self.volume}, Date: {self.date_time}"


class OhlcData:
    def __init__(self, ticker: str, data: List[Ohlcv]) -> None:
        self.ticker = ticker
        self.data = data

    @classmethod
    def default_obj(cls, ticker):
        return cls(ticker, [])

    def to_df(self) -> DataFrame:
        df = DataFrame()
        df[column_names.date] = [x.date_time.date() for x in self.data]
        df[column_names.open] = [x.open for x in self.data]
        df[column_names.high] = [x.high for x in self.data]
        df[column_names.low] = [x.low for x in self.data]
        df[column_names.close] = [x.close for x in self.data]
        df[column_names.volume] = [x.volume for x in self.data]
        df.sort_values(by=column_names.date, inplace=True, ascending=True)  # Sort by date desc
        df.reset_index(inplace=True, drop=True)  # Reset index
        return df

    @classmethod
    def from_json(cls, ticker: str, candles_data):
        # List to store OHLCV objects
        ohlcvs = []

        # Iterate through the "candles" array and convert each row to OHLCV objects
        date_format = "%Y-%m-%dT%H:%M:%S%z"
        for candle in candles_data:
            timestamp = datetime.strptime(candle[0], date_format)
            open_price = candle[1]
            high = candle[2]
            low = candle[3]
            close = candle[4]
            volume = candle[5]

            ohlcv_obj = Ohlcv(open_price, high, low, close, volume, timestamp)
            ohlcvs.append(ohlcv_obj)
        return OhlcData(ticker, ohlcvs)

    @classmethod
    def from_kite_trade_api_response(cls, ticker: str, response: list[dict[str, datetime]]):
        ohlcvs = []
        for line in response:
            open = line[column_names.open]
            high = line[column_names.high]
            low = line[column_names.low]
            close = line[column_names.close]
            volume = line[column_names.volume]
            timestamp = line[column_names.date]
            ohlcv_obj = Ohlcv(open, high, low, close, volume, timestamp)
            ohlcvs.append(ohlcv_obj)
        return OhlcData(ticker, ohlcvs)

    def get_last_price(self):
        # data might not be sorted. Iterate through the data and get the last price
        last_price = None
        date = None
        for ohlcv in self.data:
            if date is None:
                date = ohlcv.date_time.date()
                last_price = ohlcv.close
            elif ohlcv.date_time.date() > date:
                last_price = ohlcv.close
                date = ohlcv.date_time.date()
        return last_price
