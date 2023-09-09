from abc import ABC, abstractmethod
from enum import Enum


class MarketRegime(Enum):
    BULL = 1
    BEAR = 2
    NEUTRAL = 3
    # Sideways markets are good for momentum strategies


class MarketRegimeIndicatorType(Enum):
    LONG_TERM = 1
    SHORT_TERM = 2


class MarketRegimeFilter(ABC):
    def __init__(self, indicator_type: MarketRegimeIndicatorType):
        self.indicator_type = indicator_type

    @abstractmethod
    def is_allowed(self) -> MarketRegime:
        pass


class LongTermMovingAverageMarketRegimeFilter(MarketRegimeFilter):
    def __init__(self, num_days: int = 200):
        super().__init__(MarketRegimeIndicatorType.LONG_TERM)
        self.num_days = num_days

    def is_allowed(self) -> MarketRegime:
        pass
