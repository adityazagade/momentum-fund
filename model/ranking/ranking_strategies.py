import logging
from abc import ABC, abstractmethod
from datetime import date, timedelta

import numpy as np
import pandas as pd
from pandas import DataFrame
from sklearn.metrics import r2_score

import constants.column_names as column_names
from constants import constants
from model.Ohlcv import OhlcData
from model.ranking.ranking_result import RankingTable
from services.ticker_historical_data import TickerDataService


class RankingStrategy(ABC):

    def __init__(self) -> None:
        super().__init__()
        self.ticker_data_service = TickerDataService()
        self.logger = logging.getLogger(__name__)

    @abstractmethod
    def rank(self, stock_universe: list[str]) -> RankingTable:
        pass


class VolatilityAdjustedReturnsRankingStrategy(RankingStrategy):
    def __init__(self,
                 num_days: int = 90,
                 default_historical_lookup_days: int = 365,
                 max_gap_percent=20,
                 ticker_ema_span=100):
        super().__init__()
        self.default_historical_lookup_days = default_historical_lookup_days
        self.ranking_file_name = constants.RANKING_FILE_NAME
        self.num_days = num_days
        self.ticker_ema_span = ticker_ema_span
        self.max_gap_up_percent = max_gap_percent

    def rank(self, stock_universe: list[str]) -> DataFrame:
        # 1. get the last 1-year data for each stock in the stock universe
        # 2. A stock must trade over 'ticker_ema_span' days moving average to be considered a candidate
        # 3. If there has been any move larger than 15 percent in the last n days, the stock is not a buy candidate
        # 4. Annualized 'num_days' day exponential regression multiplied by coefficient of regression

        self.validate_initial_values()

        end_date = date.today()
        historical_data_lookup_start_date = date.today() - timedelta(self.default_historical_lookup_days)
        ohlcv_dataset = self.get_ohlc_data(end_date, historical_data_lookup_start_date, stock_universe)

        # Get the count of rows where date > start_date
        # num_rows = (final_df[column_names.date_col] > start_date).sum()
        num_rows = self.num_days  # (final_df[column_names.date_col] > start_date).sum()
        columns = ['ticker', 'slope', 'annualised_slope', 'r2', 'trend', 'max_gap_up', 'last_close', 'score',
                   'included']
        result_df = pd.DataFrame(columns=columns)

        for ohlcv_data in ohlcv_dataset:
            data_df = ohlcv_data.to_df()
            ticker = ohlcv_data.ticker

            # Count the number of rows in the dataframe and if less than self.num_days, skip the stock
            if len(data_df) < self.ticker_ema_span:
                print('Skipping ' + ticker + ' as it has less than ' + str(self.ticker_ema_span) + ' rows')
                continue

            self.calculate_trend(data_df)
            self.calculate_percent_change(data_df)

            df_n = data_df.iloc[-1 * num_rows:]
            df_n.reset_index(inplace=True, drop=True)

            slope, r2 = self.get_slope_and_r2(df_n)
            annualised_slope = ((np.exp(slope) ** 250) - 1) * 100
            trend = int(df_n.iloc[-1][column_names.trend])
            max_gap_up = float(df_n[column_names.percent_chg_col].max())
            last_close = df_n.iloc[-1][column_names.close]
            included = False
            if trend == 1 and max_gap_up < self.max_gap_up_percent:
                included = True

            new_row = {'ticker': ticker,
                       'slope': slope,
                       'annualised_slope': annualised_slope,
                       'r2': r2,
                       'trend': trend,
                       'max_gap_up': max_gap_up,
                       'last_close': last_close,
                       'score': r2 * annualised_slope,
                       'included': included}
            result_df.loc[len(result_df)] = new_row

        result_df.sort_values(by=['score'], ascending=False, inplace=True)
        result_df.reset_index(inplace=True, drop=True)
        self.save_ranking_results(result_df)
        return RankingTable.from_df(result_df)

    @staticmethod
    def get_slope_and_r2(df_n):
        y_actual_df = df_n[column_names.close]
        x_df = df_n.index + 1  # x-axis
        log_y_df = np.log(y_actual_df)  # y-axis
        # 1 degree polyfit. Basically a linear regression
        fit = np.polyfit(x_df, log_y_df, 1)
        log_y_predicted_df = fit[0] * x_df + fit[1]
        # Calculate the R-squared value using y_log & predicted_y_log
        r_squared = r2_score(log_y_df, log_y_predicted_df)
        return fit[0], r_squared

    def get_ohlc_data(self, end_date, historical_data_lookup_start_date, stock_universe) -> list[OhlcData]:
        ohlcv_dataset = []
        for stock in stock_universe:
            ohlcv_data = self.ticker_data_service.get_data(stock, historical_data_lookup_start_date, end_date)
            ohlcv_dataset.append(ohlcv_data)
        return ohlcv_dataset

    def validate_initial_values(self):
        # Check that the default_historical_lookup_days is greater than num_days
        if self.default_historical_lookup_days < self.num_days:
            raise ValueError("default_historical_lookup_days must be greater than num_days")
        # Check that the ticker_ema_span is less than the num_days
        if self.ticker_ema_span < self.num_days:
            raise ValueError("ticker_ema_span must be less than num_days")

    def calculate_trend(self, data_df: DataFrame):
        data_df[column_names.ema] = data_df[column_names.close].ewm(span=self.ticker_ema_span,
                                                                    adjust=False).mean()
        data_df[column_names.trend] = data_df.apply(
            lambda row: 1 if row[column_names.close] - row[column_names.ema] > 0 else (
                -1 if row[column_names.close] - row[column_names.ema] < 0 else 0), axis=1)

    def save_ranking_results(self, ranking_result_df: DataFrame):
        file_name = self.ranking_file_name
        ranking_result_df.to_csv(file_name, index=False)

    @staticmethod
    def calculate_percent_change(data_df: DataFrame):
        close_ = data_df[column_names.close]
        prior_close = close_.shift(1)
        data_df[column_names.percent_chg_col] = ((close_ - prior_close) / prior_close) * 100


class MomentumMeasureStrategy(ABC):
    pass


class ExponentialRegressionMomentumMeasureStrategy(MomentumMeasureStrategy):
    pass
