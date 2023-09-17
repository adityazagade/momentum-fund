import logging
import pandas as pd
from model.position_sizing.position_sizing_result import PositionSizingResult
from model.ranking.ranking_result import RankingResult


class Result:
    def __init__(self) -> None:
        super().__init__()
        self.rows: list[ResultRow] = []

    def __str__(self) -> str:
        return '\n'.join([str(row) for row in self.rows])

    def save(self):
        # save results as csv file in filesystem. Results are stored in result.csv
        # file in the root directory of the project.
        data_frame = pd.DataFrame()
        data_frame['symbol'] = [row.symbol for row in self.rows]
        data_frame['rank'] = [row.rank for row in self.rows]
        data_frame['score'] = [row.score for row in self.rows]
        data_frame['weight'] = [row.weight * 100 for row in self.rows]
        data_frame.sort_values(by=['rank'], inplace=True)
        data_frame.to_csv('result.csv', index=False)


class ResultRow:
    def __init__(self, symbol: str, rank: int, score: float, weight: float) -> None:
        super().__init__()
        self.symbol = symbol
        self.rank = rank
        self.score = score
        self.weight = weight

    def __str__(self) -> str:
        return f'ResultRow(symbol={self.symbol}, rank={self.rank}, score={self.score}, weight={self.weight})'


class ResultBuilder:
    def __init__(self):
        self.ranking_result = None
        self.position_sizing_result = None
        self.logger = logging.getLogger(__name__)

    def with_ranking_results(self, ranking_result: RankingResult) -> 'ResultBuilder':
        self.ranking_result = ranking_result
        return self

    def with_position_sizing_result(self, position_sizing_result: PositionSizingResult) -> 'ResultBuilder':
        self.position_sizing_result = position_sizing_result
        return self

    def build(self) -> Result:
        result = Result()
        for row in self.ranking_result.rows:
            weight = self.position_sizing_result.get_weight(row.symbol)
            if weight > 0:
                result_row = ResultRow(row.symbol, row.rank, round(row.score, 2), round(weight, 2))
                result.rows.append(result_row)
        return result
