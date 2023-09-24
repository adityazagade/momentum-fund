from model.portfolio.portfolio import Portfolio
from model.utils import rounding_function


class RebalancingResult:
    def __init__(self) -> None:
        super().__init__()
        self.portfolio: Portfolio = Portfolio(name='self_momentum')
        self.stocks_to_sell = []
        self.stocks_to_buy = []
        self.stocks_to_reduce = []
        self.stocks_to_increase = []

    def add_stock_to_buy(self, ticker, num_stocks_to_buy, weight):
        self.stocks_to_buy.append({
            'ticker': ticker,
            'num_stocks_to_buy': num_stocks_to_buy,
            'weight': rounding_function(weight)
        })

    def to_dict(self, last_close_data: dict = None):
        return {
            'portfolio': self.portfolio.to_dict(last_close_data),
            'stocks_to_sell': self.stocks_to_sell,
            'stocks_to_buy': self.stocks_to_buy,
            'stocks_to_reduce': self.stocks_to_reduce,
            'stocks_to_increase': self.stocks_to_increase
        }

    def add_stock_to_reduce(self, ticker, num_stocks_to_sell, last_close, old_weight, new_weight):
        self.stocks_to_reduce.append({
            'ticker': ticker,
            'num_stocks_to_sell': num_stocks_to_sell,
            'last_close': last_close,
            'old_weight': rounding_function(old_weight),
            'new_weight': rounding_function(new_weight)
        })

    def add_stock_to_increase(self, ticker, num_stocks_to_buy, last_close, old_weight, new_weight):
        self.stocks_to_increase.append({
            'ticker': ticker,
            'num_stocks_to_buy': num_stocks_to_buy,
            'last_close': last_close,
            'old_weight': rounding_function(old_weight),
            'new_weight': rounding_function(new_weight)
        })

    def add_stocks_to_sell(self, ticker):
        self.stocks_to_sell.append({
            'ticker': ticker
        })
