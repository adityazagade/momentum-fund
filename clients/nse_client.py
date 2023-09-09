from nsepy import get_history


class NSEClient:

    def __init__(self) -> None:
        super().__init__()
        self.get_history = get_history

    def get_data(self, symbol, start_date, end_date):
        data = self.get_history(symbol=symbol, start=start_date, end=end_date)
        return data
