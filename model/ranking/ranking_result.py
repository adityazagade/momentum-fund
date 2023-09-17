class RankingResultRow:
    def __init__(self, symbol: str, rank: int, score: float):
        super().__init__()
        self.symbol = symbol
        self.rank = rank
        self.score = score

    def __str__(self) -> str:
        return f'{self.symbol}: {self.rank} ({self.score})'


class RankingResult:
    def __init__(self, rows: list[RankingResultRow]):
        super().__init__()
        self.rows = rows

    @classmethod
    def from_df(cls, sym_param_df):
        rows = []
        for index, row in sym_param_df.iterrows():
            rows.append(RankingResultRow(row['symbol'], index + 1, row['score']))
        return cls(rows)

    def __str__(self) -> str:
        return '\n'.join([str(row) for row in self.rows])
