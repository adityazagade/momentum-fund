from abc import ABC, abstractmethod
from enum import Enum
from datetime import date, timedelta
from typing import List
import logging

from services.ticker_historical_data import TickerDataService


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
        self.ticker_data_service = TickerDataService()

    @abstractmethod
    def is_allowed(self) -> MarketRegime:
        pass


class LongTermMovingAverageMarketRegimeFilter(MarketRegimeFilter):
    def __init__(self,
                 index='NIFTY 50',
                 index_ema_span=200,
                 default_historical_lookup_days=365):
        super().__init__(MarketRegimeIndicatorType.LONG_TERM)
        self.index_ema_span = index_ema_span
        self.default_historical_lookup_days = default_historical_lookup_days
        self.index = index
        if self.default_historical_lookup_days < self.index_ema_span:
            message = "Default_historical_lookup_days must be greater than index_ema_span"
            raise ValueError(message)

    def is_allowed(self) -> MarketRegime:
        end_date = date.today()
        historical_data_lookup_start_date = date.today() - timedelta(self.default_historical_lookup_days)

        index_ohlcv_data = self.ticker_data_service.get_data(self.index, historical_data_lookup_start_date, end_date)
        index_ohlc_df = index_ohlcv_data.to_df()

        close_col = 'close'

        final_df = index_ohlc_df.copy()

        # rename the 'close' column to index_close
        final_df.rename(columns={close_col: 'index_close'}, inplace=True)

        # calculate the exponential moving average of the index
        final_df['index_ewm'] = final_df['index_close'].ewm(span=self.index_ema_span, adjust=False).mean()

        # Determine the trend 1 means bullish, -1 means bearish
        final_df['index_trend'] = final_df.apply(
            lambda row: 1 if row['index_close'] > row['index_ewm'] else (
                -1 if row['index_close'] < row['index_ewm'] else 0), axis=1)

        # Get the last row
        last_row = final_df.iloc[-1]
        # Determine the market regime
        if last_row['index_trend'] == 1:
            return MarketRegime.BULL
        elif last_row['index_trend'] == -1:
            return MarketRegime.BEAR
        else:
            return MarketRegime.NEUTRAL
