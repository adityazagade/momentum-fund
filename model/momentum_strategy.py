import logging
from datetime import date

from model.market_regime_filter import MarketRegimeFilter
from model.portfolio.portfolio import Portfolio
from model.portfolio_rebalancing import PortfolioRebalancingStrategy
from model.position_rebalancing import PositionRebalancingStrategy
from model.position_sizing.position_sizing_strategies import PositionSizingStrategy
from model.ranking.ranking_strategies import RankingStrategy
from model.results import ResultBuilder, Result
from model.scheduling.frequency import DayOfWeek


class MomentumStrategy:
    def __init__(self,
                 trade_day: DayOfWeek,
                 ranking_strategy: RankingStrategy,
                 position_sizing_strategy: PositionSizingStrategy,
                 market_regime_filter: MarketRegimeFilter,
                 position_rebalancing_strategy: PositionRebalancingStrategy,
                 portfolio_rebalancing_strategy: PortfolioRebalancingStrategy
                 ):
        self.position_sizing_strategy = position_sizing_strategy
        self.logger = logging.getLogger(__name__)
        self.trade_day = trade_day
        self.market_regime_filter = market_regime_filter
        self.position_rebalancing_strategy = position_rebalancing_strategy
        self.portfolio_rebalancing_strategy = portfolio_rebalancing_strategy
        self.ranking_strategy = ranking_strategy

    def execute(self, stock_universe: list[str], current_portfolio: Portfolio) -> None:
        self.logger.info("Executing Momentum strategy")

        # 1. We only trade on a specific day of the week
        today = date.today()
        if today.weekday() != self.trade_day.value:
            self.logger.info("Today is not a trade day. Today is %s, skip execution", today)
            return

        # 2. Rank all stocks in the universe based on momentum
        ranking_results = self.ranking_strategy.rank(stock_universe)

        # 3. Calculate position sizes based on 10 basis points.
        position_sizing_result = self.position_sizing_strategy.calculate_position_sizes(ranking_results)

        result = ResultBuilder() \
            .with_ranking_results(ranking_results) \
            .with_position_sizing_result(position_sizing_result) \
            .build()

        self.print_and_save(result)

        # 4. Check Index filter
        if not self.market_regime_filter.is_allowed():
            self.logger.info("Market regime does not allow any buying. Skip execution")
            return

        self.logger.info("Market regime allows buying. Proceeding with execution")

        # 6. Rebalance portfolio every wednesday
        # 7. Rebalance position every second wednesday

    def print_and_save(self, result: Result):
        self.logger.info(result)
        self.logger.info("Saving results to filesystem")
        result.save()
