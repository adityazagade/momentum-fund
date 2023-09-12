class RankingResultRow:
    def __init__(self, symbol: str, rank: int, score: float):
        super().__init__()
        self.symbol = symbol
        self.rank = rank
        self.score = score


class RankingResult:
    def __init__(self, rows: list[RankingResultRow]):
        super().__init__()
        self.rows = rows
