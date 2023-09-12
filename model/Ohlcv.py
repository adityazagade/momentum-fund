from datetime import datetime

from pandas import DataFrame
from typing import List


class Ohlcv:
    def __init__(self, open, high, low, close, volume, date_time: datetime) -> None:
        super().__init__()
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.date_time = date_time

    def __str__(self) -> str:
        return f"Open: {self.open}, High: {self.high}, Low: {self.low}, Close: {self.close}, Volume: {self.volume}, Date: {self.date_time}"


class OhlcData:
    def __init__(self, data: List[Ohlcv]) -> None:
        self.data = data

    @classmethod
    def default_obj(cls):
        return cls([])

    def to_df(self) -> DataFrame:
        df = DataFrame()
        df["date"] = [x.date_time.date() for x in self.data]
        df["open"] = [x.open for x in self.data]
        df["high"] = [x.high for x in self.data]
        df["low"] = [x.low for x in self.data]
        df["close"] = [x.close for x in self.data]
        df["volume"] = [x.volume for x in self.data]
        df.sort_values(by="date", inplace=True, ascending=True)  # Sort by date desc
        df.reset_index(inplace=True, drop=True)  # Reset index
        return df

    @classmethod
    def from_json(cls, response_json):
        # Extract the "candles" array from the JSON data
        candles_data = response_json["data"]["candles"]
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
        return OhlcData(ohlcvs)

    @classmethod
    def from_kite_trade_api_response(cls, response):
        ohlcvs = []
        for line in response:
            open_price = line["open"]
            high = line["high"]
            low = line["low"]
            close = line["close"]
            volume = line["volume"]
            timestamp = line["date"]
            ohlcv_obj = Ohlcv(open_price, high, low, close, volume, timestamp)
            ohlcvs.append(ohlcv_obj)
        return OhlcData(ohlcvs)
