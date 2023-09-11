import logging
from datetime import date

from pandas import DataFrame
from clients.nse_client import NSEClient
from model.Ohlcv import OhlcData
from repositories.ohlc_repo import OhlcRepository
from services.kite_connect_service import KiteConnectService

logging.basicConfig(level=logging.DEBUG)


class TickerDataService:
    def __init__(self):
        self.repository = OhlcRepository()
        self.client = NSEClient()
        self.kite_service = KiteConnectService()

    def get_data(self, ticker: str, start_date: date, end_date: date) -> OhlcData:
        return self.kite_service.get_data(ticker, start_date, end_date)

    def get_data_from_db(self, ticker: str, start_date: date, end_date: date) -> OhlcData:
        """Get data from database: Not implemented yet"""
        return self.repository.get_data_from_db(ticker, start_date, end_date)

    def get_data_from_api(self, ticker: str, start_date: date, end_date: date) -> OhlcData:
        """Get data from database: There is issue with nsepy library. It is not returning data for some stocks"""
        return self.client.get_data(ticker, start_date, end_date)
