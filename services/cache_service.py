import logging
from datetime import date

from model.Ohlcv import OhlcData


class CacheService:
    instance = None

    def __init__(self) -> None:
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.cache = {}

    def is_data_present(self, symbol: str, start_date: date, end_date: date) -> bool:
        self.logger.info(f'Checking if data is present in cache for {symbol} from {start_date} to {end_date}')
        key = f'{symbol}_{start_date}_{end_date}'
        return key in self.cache

    def get_data(self, symbol: str, start_date: date, end_date: date) -> OhlcData:
        self.logger.info(f'Fetching data from cache for {symbol} from {start_date} to {end_date}')
        key = f'{symbol}_{start_date}_{end_date}'
        return self.cache[key]

    def save_data(self, symbol: str, start_date: date, end_date: date, data: OhlcData) -> None:
        self.logger.info(f'Saving data to cache for {symbol} from {start_date} to {end_date}')
        key = f'{symbol}_{start_date}_{end_date}'
        self.cache[key] = data

    @classmethod
    def get_instance(cls):
        if cls.instance is None:
            cls.instance = CacheService()
        return cls.instance
