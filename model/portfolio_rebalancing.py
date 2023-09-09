from abc import ABC, abstractmethod

from model.scheduling.schedule import Schedule


class PortfolioRebalancingStrategy(ABC):
    """ Portfolio Rebalancing is how you change your stock portfolio over time"""

    def __init__(self, schedule: Schedule):
        self.schedule = schedule

    @abstractmethod
    def rebalance_portfolio(self, data):
        pass


class PortfolioRebalancingStrategyStrategyImpl(PortfolioRebalancingStrategy):
    """ e.g.
    1. We hold a portfolio of 20 stocks and require that the stocks must remain in the top 30
    2. When we do a portfolio rebalance, each stop must be in the top 20% of the universe of stocks or
    if it trades below its 100-day moving average
    """

    def rebalance_portfolio(self, data):
        pass
