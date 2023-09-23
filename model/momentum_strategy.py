import logging
from datetime import date
from typing import Optional

from model.market_regime_filter import MarketRegimeFilter
from model.portfolio.portfolio import Portfolio
from model.ranking.ranking_strategies import RankingStrategy
from model.rebalancing.portfolio_rebalancing import PortfolioRebalancingStrategy
from model.rebalancing.position_rebalancing import PositionRebalancingStrategy
from model.rebalancing.rebalancing_result import RebalancingResult
from model.scheduling.frequency import DayOfWeek


class MomentumStrategy:
    def __init__(self,
                 trade_day: DayOfWeek,
                 ranking_strategy: RankingStrategy,
                 market_regime_filter: MarketRegimeFilter,
                 position_rebalancing_strategy: PositionRebalancingStrategy,
                 portfolio_rebalancing_strategy: PortfolioRebalancingStrategy
                 ):
        self.logger = logging.getLogger(__name__)
        self.trade_day = trade_day
        self.market_regime_filter = market_regime_filter
        self.position_rebalancing_strategy = position_rebalancing_strategy
        self.portfolio_rebalancing_strategy = portfolio_rebalancing_strategy
        self.ranking_strategy = ranking_strategy

    def execute(self, stock_universe: list[str], current_portfolio: Portfolio) -> Optional[RebalancingResult]:
        self.logger.info("Executing Momentum strategy")

        # 1. We only trade on a specific day of the week
        today = date.today()
        if today.weekday() != self.trade_day.value:
            self.logger.info("Today is not a trade day. Today is %s, skip execution", today)
            return

        # 2. Rank all stocks in the universe based on momentum
        ranking_table = self.ranking_strategy.rank(stock_universe)

        # 3. Rebalance portfolio
        rebalancing_result = self.portfolio_rebalancing_strategy.rebalance_portfolio(
            current_portfolio,
            ranking_table)

        updated_portfolio = rebalancing_result.portfolio
        updated_portfolio.save()
        # 4. Rebalance position every second wednesday
        return rebalancing_result
