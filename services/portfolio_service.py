from datetime import date
from model.market_regime_filter import LongTermMovingAverageMarketRegimeFilter
from model.momentum_strategy import MomentumStrategy
from model.portfolio_rebalancing import PortfolioRebalancingStrategyStrategyImpl
from model.position_rebalancing import VolatilityBasedPositionRebalancingStrategy
from model.position_sizing.position_sizing_strategies import VolatilityBasedPositionSizingStrategy
from model.ranking.ranking_strategies import VolatilityAdjustedReturnsRankingStrategy
from model.scheduling.frequency import Frequency, DayOfWeek
from model.scheduling.schedule import Schedule
import pandas as pd


class PortfolioService:
    def get_current_portfolio(self):
        pass

    def get_stock_universe(self) -> []:
        nifty200_constituents_df = pd.read_csv('ind_nifty200list.csv')
        list = nifty200_constituents_df['Symbol'].tolist()
        list.remove('PATANJALI')
        # list.remove('JIOFIN')
        # return list[:10]
        return list

    def init_rebalance(self):
        trade_day = DayOfWeek.TUESDAY

        stock_universe = self.get_stock_universe()

        ranking_strategy = VolatilityAdjustedReturnsRankingStrategy(num_days=60, index='NIFTY 50')
        position_size_strategy = VolatilityBasedPositionSizingStrategy()
        market_regime_filter = LongTermMovingAverageMarketRegimeFilter(num_days=200)

        position_rebalancing_strategy = VolatilityBasedPositionRebalancingStrategy(
            schedule=Schedule(
                start_date=date.today(),
                end_date=date.today(),
                frequency=Frequency.BI_WEEKLY,
                day_of_week=trade_day,
            ))

        portfolio_rebalancing_strategy = PortfolioRebalancingStrategyStrategyImpl(
            schedule=Schedule(
                start_date=date.today(),
                end_date=date.today(),
                frequency=Frequency.WEEKLY,
                day_of_week=trade_day,
            )
        )

        ms = MomentumStrategy(
            trade_day=trade_day,
            ranking_strategy=ranking_strategy,
            position_sizing_strategy=position_size_strategy,
            market_regime_filter=market_regime_filter,
            position_rebalancing_strategy=position_rebalancing_strategy,
            portfolio_rebalancing_strategy=portfolio_rebalancing_strategy
        )
        ms.execute(stock_universe)
