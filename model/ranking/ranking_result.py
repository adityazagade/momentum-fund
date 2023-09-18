class RankingTableRow:
    def __init__(self, symbol: str, rank: int, score: float, trend: int, included: int, closing_price: float):
        super().__init__()
        self.symbol = symbol
        self.rank = rank
        self.score = score
        self.trend = trend
        self.included = included
        self.closing_price = closing_price

    def __str__(self) -> str:
        return f'{self.symbol}: {self.rank} ({self.score})'


class RankingTable:
    def __init__(self, rows: list[RankingTableRow]):
        super().__init__()
        self.rows = rows

    @classmethod
    def from_df(cls, sym_param_df):
        rows = []
        for index, row in sym_param_df.iterrows():
            rows.append(RankingTableRow(row['symbol'], index + 1, row['score'], row['trend'], row['included'], row['last_close']))
        return cls(rows)

    def __str__(self) -> str:
        return '\n'.join([str(row) for row in self.rows])
