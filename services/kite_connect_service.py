from model.Ohlcv import OhlcData
from services.kite_client import KiteClient, HttpKiteClient, KiteSDKClient


class KiteConnectService:
    def __init__(self) -> None:
        super().__init__()
        self.kite_client = HttpKiteClient()
        # self.kite_client = KiteSDKClient()

    def get_data(self, ticker, start_date, end_date) -> OhlcData:
        return self.kite_client.get_data(ticker, start_date, end_date)
