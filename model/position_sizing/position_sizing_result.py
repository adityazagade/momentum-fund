class PositionSizingResultRow:
    def __init__(self, symbol: str, weight: float, atr: float, last_close: float) -> None:
        super().__init__()
        self.symbol = symbol
        self.weight = weight
        self.atr = atr
        self.last_close = last_close


class PositionSizingResult:
    def __init__(self) -> None:
        super().__init__()
        self.rows: list[PositionSizingResultRow] = []

    def add_position(self, symbol, weight, atr, last_close):
        self.rows.append(PositionSizingResultRow(symbol, weight, atr, last_close))

    def get_weight(self, symbol) -> float:
        for row in self.rows:
            if row.symbol == symbol:
                return row.weight
        return 0.0

    def get_atr(self, symbol) -> float:
        for row in self.rows:
            if row.symbol == symbol:
                return row.atr

    def get_last_close(self, symbol) -> float:
        for row in self.rows:
            if row.symbol == symbol:
                return row.last_close
