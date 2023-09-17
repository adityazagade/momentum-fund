import logging
from datetime import date

from config.app_config import AppConfig
from model.market_regime_filter import LongTermMovingAverageMarketRegimeFilter
from model.momentum_strategy import MomentumStrategy
from model.portfolio_rebalancing import PortfolioRebalancingStrategyStrategyImpl
from model.position_rebalancing import VolatilityBasedPositionRebalancingStrategy
from model.position_sizing.position_sizing_strategies import EqualRiskPositionSizingStrategy
from model.ranking.ranking_strategies import VolatilityAdjustedReturnsRankingStrategy
from model.scheduling.frequency import Frequency, DayOfWeek
from model.scheduling.schedule import Schedule
from services.index_service import IndexDataService
from services.portfolio_service import PortfolioService

TRADE_DAY_KEY = 'trade_day'

PROPERTIES_FILE = 'app.properties'

STOCK_UNIVERSE_INDEX_KEY = 'stock_universe_index'


class StrategyExecutor:
    def __init__(self) -> None:
        super().__init__()
        self.app_config = AppConfig(PROPERTIES_FILE)
        self.logger = logging.getLogger(__name__)
        self.portfolio_service = PortfolioService()
        self.index_service = IndexDataService()

    def execute(self):
        self.logger.info('Executing strategy executor')

        current_portfolio = self.portfolio_service.get_portfolio()
        self.logger.info(f'Current portfolio: {current_portfolio}')

        trade_day = DayOfWeek.from_string(self.app_config.get(TRADE_DAY_KEY), default=DayOfWeek.WEDNESDAY)
        self.logger.info(f'Trade day: {trade_day}')

        num_historical_lookup_days = int(self.app_config.get_or_default('num_historical_lookup_days', default=365))

        ranking_strategy = \
            VolatilityAdjustedReturnsRankingStrategy(num_days=90,
                                                     default_historical_lookup_days=num_historical_lookup_days,
                                                     max_gap_percent=20,
                                                     ticker_ema_span=100
                                                     )

        position_size_strategy = EqualRiskPositionSizingStrategy(
            default_historical_lookup_days=num_historical_lookup_days,
            atr_period=20,
            risk_factor=0.001
        )

        market_regime_filter = LongTermMovingAverageMarketRegimeFilter(index='NIFTY 50',
                                                                       index_ema_span=200,
                                                                       default_historical_lookup_days=365)

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

        index = self.app_config.get(STOCK_UNIVERSE_INDEX_KEY)
        stock_universe = self.index_service.get_index_constituents(index)

        ms.execute(stock_universe, current_portfolio)
