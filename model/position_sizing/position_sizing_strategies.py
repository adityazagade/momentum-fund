from abc import ABC, abstractmethod


class PositionSizingStrategy(ABC):
    @abstractmethod
    def calculate_position_sizes(self, ranking_results):
        pass


class VolatilityBasedPositionSizingStrategy(PositionSizingStrategy):

    def calculate_position_sizes(self, ranking_results):
        pass
