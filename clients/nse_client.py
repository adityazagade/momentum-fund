import logging

from nsepy import get_history
import pandas as pd


class NSEClient:

    def __init__(self) -> None:
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.get_history = get_history

    def get_data(self, symbol, start_date, end_date):
        data = self.get_history(symbol=symbol, start=start_date, end=end_date)
        return data

    def get_stock_universe(self, index: str):
        self.logger.info(f'Fetching stock universe for index: {index}')
        url_template = "https://archives.nseindia.com/content/indices/ind_{index}list.csv"
        url = url_template.format(index=index.lower().replace(' ', ''))
        df = pd.read_csv(url)
        return df["Symbol"].tolist()
