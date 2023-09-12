from model.portfolio.holding import Holding
from pandas import DataFrame


class Portfolio:
    def __init__(self, name):
        self.name = name
        self.holdings = []

    def add_holding(self, holding: Holding):
        self.holdings.append(holding)

    @staticmethod
    def from_df(df: DataFrame):
        portfolio = Portfolio(name='self_momentum')
        for row in df.iterrows():
            holding = Holding(row[0], row[1])
            portfolio.add_holding(holding)
        return portfolio

    def __str__(self) -> str:
        return f'Portfolio: {self.name}, Holdings: {self.holdings}'