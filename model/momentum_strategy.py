import logging
from datetime import date
from typing import Optional

from model.market_regime_filter import MarketRegimeFilter
from model.portfolio.portfolio import Portfolio
from model.ranking.ranking_strategies import RankingStrategy
from model.rebalancing.portfolio_rebalancing import PortfolioRebalancingStrategy
from model.rebalancing.rebalancing_result import RebalancingResult
from model.scheduling.frequency import DayOfWeek
from model.scheduling.schedule import Schedule


class MomentumStrategy:
    def __init__(self,
                 trade_day: DayOfWeek,
                 ranking_strategy: RankingStrategy,
                 market_regime_filter: MarketRegimeFilter,
                 portfolio_rebalancing_strategy: PortfolioRebalancingStrategy,
                 portfolio_rebalance_schedule: Schedule
                 ):
        self.logger = logging.getLogger(__name__)
        self.trade_day = trade_day
        self.market_regime_filter = market_regime_filter
        self.portfolio_rebalancing_strategy = portfolio_rebalancing_strategy
        self.ranking_strategy = ranking_strategy
        self.portfolio_rebalance_schedule = portfolio_rebalance_schedule

    def execute(self,
                stock_universe: list[str],
                current_portfolio: Portfolio,
                cash_flow: float) -> Optional[RebalancingResult]:
        self.logger.info("Executing Momentum strategy")

        # 1. We only trade on a specific day of the week
        today = date.today()
        if today.weekday() != self.trade_day.value:
            self.logger.info("Today is not a trade day. Today is %s, skip execution", today)
            return

        # 2. Rank all stocks in the universe based on momentum
        ranking_table = self.ranking_strategy.rank(stock_universe)

        rebalancing_result = None

        # 3. Rebalance portfolio if schedule matches today
        if self.portfolio_rebalance_schedule.matches(today):
            rebalancing_result = self.portfolio_rebalancing_strategy.rebalance_portfolio(
                current_portfolio,
                ranking_table,
                cash_flow)

        updated_portfolio = rebalancing_result.portfolio
        updated_portfolio.save()

        # 4. Rebalance position every second wednesday
        last_close_data = {}
        for row in ranking_table.rows:
            last_close_data[row.symbol] = row.closing_price
        return rebalancing_result.to_dict(last_close_data)
