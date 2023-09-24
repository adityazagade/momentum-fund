import datetime

import pandas as pd

from model.portfolio.holding import Holding
from pandas import DataFrame

from model.utils import rounding_function


class Portfolio:
    def __init__(self, name):
        self.name = name
        self.holdings: list[Holding] = []
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

    def sell_stock(self, symbol: str, selling_price: float, quantity=None) -> None:
        for holding in self.holdings:
            if holding.symbol == symbol:
                if quantity is None or quantity == holding.quantity:
                    quantity = holding.quantity
                    self.holdings.remove(holding)
                elif quantity > holding.quantity:
                    raise ValueError(f'Cannot sell {quantity} of {symbol} because you only have {holding.quantity}')
                else:
                    holding.quantity -= quantity
                self.cash += quantity * selling_price

    def is_present(self, symbol: str) -> bool:
        for holding in self.holdings:
            if holding.symbol == symbol:
                return True
        return False

    def buy_stock(self, symbol: str, quantity: int, price: float):
        if self.is_present(symbol):
            # add to existing holding
            for holding in self.holdings:
                if holding.symbol == symbol:
                    holding.quantity += quantity
        else:
            # create a new holding
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
        df.loc[len(df)] = ['LIQUIDBEES', self.cash / 1000]
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

    def to_dict(self, last_close_data: dict = None):
        # iterate over holdings and create a dictionary
        account_value = 0
        if last_close_data is not None:
            account_value = self.get_account_value(last_close_data)

        holdings = []
        for holding in self.holdings:
            weight = None
            close = None
            if last_close_data is not None:
                weight = holding.quantity * last_close_data[holding.symbol] / account_value
                close = last_close_data[holding.symbol]
            weight_str = '-'
            close_str = '-'
            if weight is not None:
                weight_str = f'{rounding_function(weight * 100)}%'
            if close is not None:
                close_str = f'{rounding_function(close)}'

            holdings.append(
                {'symbol': holding.symbol, 'quantity': holding.quantity, 'weight': weight_str, 'close': close_str}
            )
        if account_value == 0:
            account_value_str = '-'
            cash_weight_str = '-'
        else:
            account_value_str = rounding_function(account_value)
            cash_weight_str = f'{rounding_function(self.cash * 100 / account_value)}%'
        return {'name': self.name,
                'holdings': holdings,
                'cash': {
                    'value': rounding_function(self.cash),
                    'weight': cash_weight_str
                },
                'account_value': account_value_str
                }

    def get_tickers(self):
        return [holding.symbol for holding in self.holdings]
