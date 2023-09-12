class Holding:
    def __init__(self, symbol, quantity):
        self.symbol = symbol
        self.quantity = quantity

    def __str__(self) -> str:
        return f'{self.symbol} - {self.quantity}'
