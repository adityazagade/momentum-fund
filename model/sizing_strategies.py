from abc import ABC, abstractmethod


class PositionSizeStrategy(ABC):
    @abstractmethod
    def allocate_weights(self, data):
        pass


class EqualRiskContributionPositionSizeStrategy(PositionSizeStrategy):
    """ Uses Risk Parity allocation strategy
        shares = (account_value * risk_factor / ATR) , where ATR is the average true range of the stock
    """

    def allocate_weights(self, data):
        pass
