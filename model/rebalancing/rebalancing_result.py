from model.portfolio.portfolio import Portfolio


class RebalancingResult:
    def __init__(self) -> None:
        super().__init__()
        self.portfolio: Portfolio = Portfolio(name='self_momentum')
        self.stocks_to_sell = []
        self.stocks_to_buy = []

    def add_stock_to_buy(self, symbol, num_stocks_to_buy, weight):
        self.stocks_to_buy.append((symbol, num_stocks_to_buy, weight))
