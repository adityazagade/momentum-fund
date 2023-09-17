import logging
import math
from abc import ABC, abstractmethod
from datetime import date, timedelta

from model.position_sizing.position_sizing_result import PositionSizingResult
from model.ranking.ranking_result import RankingResult
from services.ticker_historical_data import TickerDataService


class PositionSizingStrategy(ABC):
    def __init__(self) -> None:
        super().__init__()
        self.logger = logging.getLogger(__name__)

    @abstractmethod
    def calculate_position_sizes(self, ranking_results):
        pass


class EqualRiskPositionSizingStrategy(PositionSizingStrategy):
    close_col = 'close'
    atr_col = 'atr'
    date_col = 'date'
    high_col = 'high'
    low_col = 'low'

    def __init__(self,
                 default_historical_lookup_days: int = 365,
                 atr_period: int = 20,
                 risk_factor: float = 0.001
                 ) -> None:
        super().__init__()
        self.ticker_data_service = TickerDataService()
        self.default_historical_lookup_days = default_historical_lookup_days
        self.atr_period = atr_period
        # Define the period for ATR calculation (e.g., 14 days)
        self.atr_period = atr_period
        self.risk_factor = risk_factor  # 1 percent risk factor

    def calculate_position_sizes(self, ranking_result: RankingResult) -> PositionSizingResult:
        self.logger.info("Calculating position sizes based on volatility")
        end_date = date.today()
        historical_data_lookup_start_date = date.today() - timedelta(self.default_historical_lookup_days)

        # allocate weights
        account_value = 10000000
        remaining_cash = account_value
        daily_risk = account_value * self.risk_factor

        position_sizing_result = PositionSizingResult()
        for row in ranking_result.rows:
            if remaining_cash > 0:
                ohlcv_data = self.ticker_data_service.get_data(row.symbol, historical_data_lookup_start_date, end_date)
                data_df = ohlcv_data.to_df()
                self.calculate_atr(data_df, self.atr_period)
                current_atr = data_df[self.atr_col].iloc[-1]
                last_close = data_df[self.close_col].iloc[-1]
                num_stocks_to_buy = math.floor(daily_risk / current_atr)
                account_value_allotted = num_stocks_to_buy * last_close
                weight = account_value_allotted / account_value
                remaining_cash = remaining_cash - account_value_allotted
                position_sizing_result.add_position(row.symbol, weight)
            else:
                weight = 0
                position_sizing_result.add_position(row.symbol, weight)

        return position_sizing_result

    def calculate_atr(self, data_df, period):
        # Calculate True Range (TR) for each row
        data_df['high-low'] = data_df[self.high_col] - data_df[self.low_col]
        data_df['high-previous-close'] = abs(data_df[self.high_col] - data_df[self.close_col].shift(1))
        data_df['low-previous-close'] = abs(data_df[self.low_col] - data_df[self.close_col].shift(1))
        # Calculate the maximum of the three TR values
        data_df['true_range'] = data_df[['high-low', 'high-previous-close', 'low-previous-close']].max(axis=1)
        # Calculate ATR using the rolling mean of the True Range
        data_df[self.atr_col] = data_df['true_range'].rolling(window=period).mean()
        # Drop the intermediate columns used for TR calculation
        data_df.drop(['high-low', 'high-previous-close', 'low-previous-close', 'true_range'], axis=1, inplace=True)
