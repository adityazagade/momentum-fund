class RankingTableRow:
    def __init__(self, symbol: str, rank: int, score: float, trend: int, included: bool, closing_price: float):
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
            rows.append(RankingTableRow(row['ticker'],
                                        index + 1,
                                        row['score'],
                                        row['trend'],
                                        row['included'],
                                        row['last_close']))
        return cls(rows)

    def __str__(self) -> str:
        return '\n'.join([str(row) for row in self.rows])

    def get_last_close(self, ticker: str) -> float:
        for row in self.rows:
            if row.symbol == ticker:
                return row.closing_price
        raise ValueError(f'Could not find ticker {ticker} in ranking table')
