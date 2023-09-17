class PositionSizingResultRow:
    def __init__(self, symbol: str, weight: float) -> None:
        super().__init__()
        self.symbol = symbol
        self.weight = weight


class PositionSizingResult:
    def __init__(self) -> None:
        super().__init__()
        self.rows = []

    def add_position(self, symbol, weight):
        self.rows.append(PositionSizingResultRow(symbol, weight))

    def get_weight(self, symbol) -> float:
        for row in self.rows:
            if row.symbol == symbol:
                return row.weight
        return 0.0
