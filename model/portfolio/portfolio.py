import datetime

import pandas as pd

from model.portfolio.holding import Holding
from pandas import DataFrame


class Portfolio:
    def __init__(self, name):
        self.name = name
        self.holdings = []
        self.cash = 0

    def add_holding(self, holding: Holding):
        self.holdings.append(holding)

    @staticmethod
    def from_df(df: DataFrame):
        portfolio = Portfolio(name='self_momentum')
        for row in df.iterrows():
            symbol = row[1]['symbol']
            quantity = row[1]['quantity']
            if symbol == 'LIQUIDBEES':
                portfolio.cash = quantity * 1000
                continue
            holding = Holding(symbol=symbol, quantity=quantity)
            portfolio.add_holding(holding)
        return portfolio

    def __str__(self) -> str:
        # print row by row and then cash
        return '\n'.join([str(holding) for holding in self.holdings]) + f'\nCash: {self.cash}'

    def sell_stock(self, symbol: str, selling_price: float) -> None:
        for holding in self.holdings:
            if holding.symbol == symbol:
                self.holdings.remove(holding)
                self.cash += holding.quantity * selling_price

    def is_present(self, symbol: str) -> bool:
        for holding in self.holdings:
            if holding.symbol == symbol:
                return True
        return False

    def buy_stock(self, symbol: str, quantity: int, price: float):
        holding = Holding(symbol=symbol, quantity=quantity)
        self.holdings.append(holding)
        self.cash -= quantity * price

    def get_account_value(self, closing_price_data):
        account_value = self.cash
        for holding in self.holdings:
            symbol = holding.symbol
            quantity = holding.quantity
            price = closing_price_data[symbol]
            account_value += quantity * price
        return account_value

    def save(self):
        # save the portfolio to a file
        # name should be portfolio_<name>_<date>.csv
        df = self.to_df()
        df.to_csv(f'portfolio_{self.name}_{datetime.date.today()}.csv', index=False)

    def to_df(self):
        # iterate over holdings and create a dataframe
        symbols = []
        quantities = []
        for holding in self.holdings:
            symbols.append(holding.symbol)
            quantities.append(holding.quantity)
        df = pd.DataFrame({'symbol': symbols, 'quantity': quantities})
        return df
