import math
import numpy as np
import pandas as pd
from pandas import DataFrame
from sklearn.metrics import r2_score
from model.ranking.ranking_result import RankingResult
from services.ticker_historical_data import TickerDataService
import logging
from abc import ABC, abstractmethod
from datetime import date, timedelta
from typing import List


class RankingStrategy(ABC):

    def __init__(self) -> None:
        super().__init__()
        self.ticker_data_service = TickerDataService()
        self.logger = logging.getLogger(__name__)

    @abstractmethod
    def rank(self, stock_universe: list[str]) -> RankingResult:
        pass


class VolatilityAdjustedReturnsRankingStrategy(RankingStrategy):
    close_col = 'close'
    atr_col = 'atr'
    trend_col = 'trend'
    ema_col = 'ema'
    percent_chg_col = 'percent_change'
    date_col = 'date'
    high_col = 'high'
    low_col = 'low'
    open_col = 'open'
    volume_col = 'volume'

    def __init__(self,
                 num_days: int = 90,
                 stock_universe: List[str] = None,
                 atr_period: int = 20,
                 default_historical_lookup_days: int = 365,
                 max_gap_percent=20,
                 risk_factor=0.001,
                 ticker_ema_span=100):
        super().__init__()
        self.default_historical_lookup_days = default_historical_lookup_days
        self.ranking_file_name = 'ranking.csv'
        self.results_dir = 'results'
        self.num_days = num_days
        self.stock_universe = stock_universe
        self.ticker_ema_span = ticker_ema_span
        # Define the period for ATR calculation (e.g., 14 days)
        self.atr_period = atr_period
        self.risk_factor = risk_factor  # 1 percent risk factor
        self.max_gap_percent = max_gap_percent

    def rank(self, stock_universe: list[str]) -> DataFrame:
        # Check that the default_historical_lookup_days is greater than num_days
        if self.default_historical_lookup_days < self.num_days:
            raise ValueError("default_historical_lookup_days must be greater than num_days")

        # Check that the ticker_ema_span is less than the num_days
        if self.ticker_ema_span < self.num_days:
            raise ValueError("ticker_ema_span must be less than num_days")

        end_date = date.today()
        historical_data_lookup_start_date = date.today() - timedelta(self.default_historical_lookup_days)
        start_date = date.today() - timedelta(self.num_days)

        final_df = pd.DataFrame()
        final_df[self.date_col] = pd.date_range(historical_data_lookup_start_date, end_date).date

        stock_universe_filtered = []
        for stock in stock_universe:
            # 1. get the last 1-year data for each stock in the stock universe
            # 2. A stock must trade over 'ticker_ema_span' days moving average to be considered a candidate
            # 3. If there has been any move larger than 15 percent in the last n days, the stock is not a buy candidate
            # 4. Annualized 'num_days' day exponential regression multiplied by coefficient of regression

            sym = stock.lower()

            sym_ema_col = sym + '_ema'
            sym_trend_col = sym + '_trend'
            sym_percent_chg_col = sym + '_percent_change'
            sym_close_col = sym + '_close'
            sym_atr_col = sym + '_atr'

            ohlcv_data = self.ticker_data_service.get_data(stock, historical_data_lookup_start_date, end_date)

            data_df = ohlcv_data.to_df()

            # Count the number of rows in the dataframe and if less than self.num_days, skip the stock
            if len(data_df) < self.ticker_ema_span:
                print('Skipping ' + stock + ' as it has less than ' + str(self.ticker_ema_span) + ' rows')
                continue

            stock_universe_filtered = stock_universe_filtered + [stock]

            self.calculate_trend(data_df)
            self.calculate_atr(data_df, self.atr_period)

            data_df.rename(columns={self.close_col: sym_close_col}, inplace=True)
            data_df.rename(columns={self.atr_col: sym_atr_col}, inplace=True)
            data_df.rename(columns={self.trend_col: sym_trend_col}, inplace=True)
            data_df.rename(columns={self.ema_col: sym_ema_col}, inplace=True)
            data_df.rename(columns={self.percent_chg_col: sym_percent_chg_col}, inplace=True)

            # Create a new dataframe with only the columns we need
            final_df = pd.merge(final_df,
                                data_df[
                                    [self.date_col,
                                     sym_close_col,
                                     sym_atr_col,
                                     sym_trend_col,
                                     sym_ema_col,
                                     sym_percent_chg_col]
                                ],
                                how='inner',
                                on=['date'])

        # Get the count of rows where date > start_date
        num_rows = (final_df[self.date_col] > start_date).sum()
        num_rows = self.num_days  # (final_df[self.date_col] > start_date).sum()

        symbols = []
        r2 = []
        slope = []
        trend = []
        max_gap_up = []
        atr = []
        included = []
        last_close = []

        for ticker in stock_universe_filtered:
            sym = ticker.lower()

            sym_trend_col = sym + '_trend'
            sym_percent_chg_col = sym + '_percent_change'
            sym_close_col = sym + '_close'
            sym_atr_col = sym + '_atr'

            symbols.append(ticker)

            i = -1 * num_rows
            df_n = final_df.iloc[i:].reset_index()

            y_actual_df = df_n[sym_close_col]

            x_df = df_n.index + 1  # x-axis
            log_y_df = np.log(y_actual_df)  # y-axis

            # 1 degree polyfit. Basically a linear regression
            fit = np.polyfit(x_df, log_y_df, 1)

            # Approach 1

            # # y = a * exp(b * x)
            # y_predicted_df = np.exp(fit[1]) * np.exp(fit[0] * x_df)
            # # Calculate the R-squared value using y_actual & y_predicted
            # r_squared = r2_score(y_actual_df, y_predicted_df)

            # Approach 2
            # y = mx + c
            log_y_predicted_df = fit[0] * x_df + fit[1]
            # Calculate the R-squared value using y_log & predicted_y_log
            r_squared = r2_score(log_y_df, log_y_predicted_df)

            trend_flag = int(df_n.iloc[-1][sym_trend_col])
            max_gap_up_percent = float(df_n[sym_percent_chg_col].max()) * 100

            ticker_atr = df_n[sym_atr_col].iloc[-1]

            slope.append(fit[0])
            r2.append(r_squared)
            trend.append(trend_flag)
            max_gap_up.append(max_gap_up_percent)
            atr.append(ticker_atr)
            last_close.append(y_actual_df.iloc[-1])

            if trend_flag == 1 and max_gap_up_percent < self.max_gap_percent:
                included.append(1)
            else:
                included.append(0)

        sym_param_df = pd.DataFrame()
        sym_param_df['symbol'] = symbols
        sym_param_df['r2'] = r2
        sym_param_df['slope'] = slope
        sym_param_df['trend'] = trend
        sym_param_df['max_gap_up'] = max_gap_up
        sym_param_df['annualised_slope'] = ((np.exp(sym_param_df['slope']) ** 250) - 1) * 100  # Annualised slope in %
        # sym_param_df['annualised_slope'] = pow(1 + sym_param_df['slope'], 250)
        sym_param_df['mul'] = sym_param_df['r2'] * sym_param_df['annualised_slope']
        sym_param_df['atr'] = atr
        sym_param_df['included'] = included
        sym_param_df['last_close'] = last_close

        sym_param_df.sort_values(by=['included', 'mul'], ascending=False, inplace=True)

        # allocate weights
        account_value = 10000000
        remaining_cash = account_value

        target_percent = []
        for index, row in sym_param_df.iterrows():
            if remaining_cash > 0 and row['included'] == 1:
                daily_risk = account_value * self.risk_factor
                ticker_atr = row['atr']
                last_close_price = row['last_close']
                num_stocks_to_buy = math.floor(daily_risk / ticker_atr)
                account_value_allotted = num_stocks_to_buy * last_close_price
                position_size = (account_value_allotted / account_value) * 100
                remaining_cash = remaining_cash - account_value_allotted
                target_percent.append(position_size)
            else:
                target_percent.append(0)

        sym_param_df['target_percent'] = target_percent
        self.save_ranking_results(sym_param_df)
        return sym_param_df

    def calculate_trend(self, data_df: DataFrame):
        data_df[self.ema_col] = data_df[self.close_col].ewm(span=self.ticker_ema_span, adjust=False).mean()
        data_df[self.percent_chg_col] = (data_df[self.close_col] - data_df[self.close_col].shift(1)) / data_df[
            self.close_col].shift(1)
        data_df[self.trend_col] = data_df.apply(
            lambda row: 1 if row[self.close_col] - row[self.ema_col] > 0 else (
                -1 if row[self.close_col] - row[self.ema_col] < 0 else 0), axis=1)

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

    def save_ranking_results(self, sym_param_df):
        sym_param_df.to_csv(self.results_dir + self.ranking_file_name, index=False)


class MomentumMeasureStrategy(ABC):
    pass


class ExponentialRegressionMomentumMeasureStrategy(MomentumMeasureStrategy):
    pass
