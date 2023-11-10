import logging
from constants import constants as constants

from datetime import date
from config.app_config import AppConfig
from model.filter.filters import IndexConstituentsFilter
from model.market_regime_filter import LongTermMovingAverageMarketRegimeFilter
from model.momentum_strategy import MomentumStrategy
from model.rebalancing.portfolio_rebalancing import PortfolioRebalancingStrategyStrategyImpl
from model.position_sizing.position_sizing_strategies import EqualRiskPositionSizingStrategy
from model.ranking.ranking_strategies import VolatilityAdjustedReturnsRankingStrategy
from model.scheduling.frequency import Frequency, DayOfWeek
from model.scheduling.schedule import Schedule
from services.index_service import IndexDataService
from services.portfolio_service import PortfolioService


class StrategyExecutor:
    """
    This class is responsible for executing the strategy
    """

    def __init__(self) -> None:
        super().__init__()
        self.app_config = AppConfig(constants.PROPERTIES_FILE)
        self.logger = logging.getLogger(__name__)
        self.portfolio_service = PortfolioService()
        self.index_service = IndexDataService()

    def execute(self, cash_flow: float = 0.0):
        """
        This method executes the strategy
        :param cash_flow: The amount of cash to be invested
        :return: Rebalancing result
        """
        self.logger.info('Executing strategy executor')

        current_portfolio = self.portfolio_service.get_portfolio()
        self.logger.info("Current portfolio: \n%s", current_portfolio)

        trade_day = DayOfWeek.from_string(self.app_config.get(constants.TRADE_DAY_KEY), default=DayOfWeek.WEDNESDAY)
        self.logger.info("Trade day: %s", trade_day)

        num_historical_lookup_days = int(self.app_config.get_or_default('num_historical_lookup_days', default=365))
        min_market_cap = int(self.app_config.get_or_default('filter.min_market_cap', default=0))

        threshold = 0.0025  # 0.25%
        ticker_ema_span = 100
        risk_factor = 0.003
        top_n_percent = 20
        num_days = 90
        max_gap_percent = 20
        atr_period = 20
        index_ema_span = 200
        default_historical_lookup_days = 365

        inception_date = date(2010, 1, 1)
        end_date = inception_date.replace(year=date.today().year + 100)

        ranking_strategy = VolatilityAdjustedReturnsRankingStrategy(
            num_days=num_days,
            default_historical_lookup_days=num_historical_lookup_days,
            max_gap_percent=max_gap_percent,
            ticker_ema_span=ticker_ema_span
        )

        position_size_strategy = EqualRiskPositionSizingStrategy(
            default_historical_lookup_days=num_historical_lookup_days,
            atr_period=atr_period,
            risk_factor=risk_factor
        )

        market_regime_filter = LongTermMovingAverageMarketRegimeFilter(
            index='NIFTY 50',
            index_ema_span=index_ema_span,
            default_historical_lookup_days=default_historical_lookup_days)

        position_rebalance_schedule = Schedule(
            start_date=inception_date,
            end_date=end_date,
            frequency=Frequency.BI_WEEKLY,
            day_of_week=trade_day,
        )

        portfolio_rebalance_schedule = Schedule(
            start_date=inception_date,
            end_date=end_date,
            frequency=Frequency.WEEKLY,
            day_of_week=trade_day,
        )

        portfolio_rebalancing_strategy = PortfolioRebalancingStrategyStrategyImpl(
            risk_factor=risk_factor,
            top_n_percent=top_n_percent,
            ticker_ema_span=ticker_ema_span,
            market_regime_filter=market_regime_filter,
            position_sizing_strategy=position_size_strategy,
            position_rebalance_schedule=position_rebalance_schedule,
            threshold=threshold
        )

        momentum_strategy = MomentumStrategy(
            trade_day=trade_day,
            ranking_strategy=ranking_strategy,
            market_regime_filter=market_regime_filter,
            portfolio_rebalancing_strategy=portfolio_rebalancing_strategy,
            portfolio_rebalance_schedule=portfolio_rebalance_schedule
        )

        index = self.app_config.get(constants.STOCK_UNIVERSE_INDEX_KEY)

        if min_market_cap:
            index_constituents_filter = IndexConstituentsFilter(min_market_cap=min_market_cap)
        else:
            index_constituents_filter = None
        stock_universe = self.index_service.get_index_constituents(index, index_filter=index_constituents_filter)

        return momentum_strategy.execute(stock_universe, current_portfolio, cash_flow)
