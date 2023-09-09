from abc import ABC, abstractmethod

from model.scheduling.schedule import Schedule


class PositionRebalancingStrategy(ABC):
    """ Position Rebalancing is how you change your position size over time"""

    @abstractmethod
    def rebalance_position(self, data):
        pass


class VolatilityBasedPositionRebalancingStrategy(PositionRebalancingStrategy):
    """ Rebalance based on volatility of the stock"""

    def __init__(self, schedule: Schedule):
        self.schedule = schedule

    def rebalance_position(self, data):
        pass
