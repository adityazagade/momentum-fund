from nsepy import get_history
import pandas as pd


class NSEClient:

    def __init__(self) -> None:
        super().__init__()
        self.get_history = get_history

    def get_data(self, symbol, start_date, end_date):
        data = self.get_history(symbol=symbol, start=start_date, end=end_date)
        return data

    @staticmethod
    def get_stock_universe(index: str):
        url_template = "https://archives.nseindia.com/content/indices/ind_{index}list.csv"
        url = url_template.format(index=index.lower().replace(' ', ''))
        df = pd.read_csv(url)
        return df["Symbol"].tolist()
