class Holding:
    def __init__(self, symbol: str, quantity: int):
        self.symbol: str = symbol
        self.quantity: int = quantity

    def __str__(self) -> str:
        return f'{self.symbol} - {self.quantity}'

    def to_dict(self):
        return {
            'symbol': self.symbol,
            'quantity': self.quantity
        }
