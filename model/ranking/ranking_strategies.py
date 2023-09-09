import math
from abc import ABC, abstractmethod
from datetime import date, timedelta
from typing import List

import numpy as np
import pandas as pd
from pandas import DataFrame
from sklearn.metrics import r2_score

from model.ranking.ranking_result import RankingResult
from services.ticker_historical_data import TickerDataService


class RankingStrategy(ABC):

    def __init__(self) -> None:
        super().__init__()
        self.ticker_data_service = TickerDataService()

    @abstractmethod
    def rank(self, stock_universe: list[str]) -> RankingResult:
        pass


class VolatilityAdjustedReturnsRankingStrategy(RankingStrategy):
    def __init__(self,
                 num_days: int = 60,
                 stock_universe: List[str] = None,
                 index: str = 'NIFTY 50',
                 atr_period: int = 14):
        super().__init__()
        self.ranking_file_name = 'ranking.csv'
        self.results_dir = 'results'
        self.num_days = num_days
        self.stock_universe = stock_universe
        self.index = index
        self.index_ema_span = 200
        self.ticker_span = 50
        # Define the period for ATR calculation (e.g., 14 days)
        self.atr_period = atr_period
        self.risk_factor = 0.001  # 1 percent risk factor

    def rank(self, stock_universe: list[str]) -> DataFrame:
        # get the last 1-year data for each stock in the stock universe
        # 1. A stock must trade over 100 days moving average to be considered a buy candidate
        # 2. If there has been any move larger than 15 percent in the last n days, the stock is not a buy candidate
        # 3. Annualized n day exponential regression multiplied by coefficient of regression

        end_date = date.today()
        one_year_back_date = date.today() - timedelta(365)

        index_ohlc_df = self.ticker_data_service.get_data(self.index, one_year_back_date, end_date)

        close_column_name_orig = 'close'

        final_df = index_ohlc_df.copy()
        final_df.rename(columns={close_column_name_orig: 'index_close'}, inplace=True)
        final_df['index_ewm'] = final_df['index_close'].ewm(span=self.index_ema_span, adjust=False).mean()

        # 1 means bullish, -1 means bearish
        final_df['index_trend'] = final_df.apply(
            lambda row: 1 if row['index_close'] - row['index_ewm'] > 0 else (
                -1 if row['index_close'] - row['index_ewm'] < 0 else 0), axis=1)

        stock_universe_filtered = []
        for stock in stock_universe:
            sym = stock.lower()
            ema_column_name = 'ema'
            trend_column_name = sym + '_trend'
            percent_chg_col_name = sym + '_percent_change'

            data_df = self.ticker_data_service.get_data(stock, one_year_back_date, end_date)
            # count the number of rows in the dataframe and if less than self.num_days, skip the stock
            if len(data_df) < self.num_days:
                continue

            stock_universe_filtered = stock_universe_filtered + [stock]
            data_df[ema_column_name] = data_df['close'].ewm(span=self.ticker_span, adjust=False).mean()
            data_df[percent_chg_col_name] = (data_df['close'] - data_df['close'].shift(1)) / data_df['close'].shift(1)

            # data_df['SMA30'] = data_df['close'].rolling(30).mean()  in case you want sma

            data_df[trend_column_name] = data_df.apply(
                lambda row: 1 if row['close'] - row[ema_column_name] > 0 else (
                    -1 if row['close'] - row[ema_column_name] < 0 else 0), axis=1)

            self.calculate_atr(data_df, self.atr_period)

            close_column_name_new = sym + '_close'
            atr_column_name = 'ATR'
            atr_column_name_new = sym + '_ATR'
            data_df.rename(columns={close_column_name_orig: close_column_name_new}, inplace=True)
            data_df.rename(columns={atr_column_name: atr_column_name_new}, inplace=True)
            final_df = pd.merge(final_df,
                                data_df[['date', close_column_name_new, trend_column_name, percent_chg_col_name, atr_column_name_new]],
                                how='left',
                                on=['date'])

        symbols = []
        r2 = []
        slope = []
        trend = []
        max_gap_up = []
        atr = []
        target_percent = []
        included = []

        account_value = 100000
        remaining_cash = account_value

        for ticker in stock_universe_filtered:
            print(ticker)
            symbols.append(ticker)

            sym = ticker.lower()
            close_column_name_new = sym + '_close'
            trend_column_name = sym + '_trend'
            percent_chg_col_name = sym + '_percent_change'
            atr_column_name_new = sym + '_ATR'

            i = -1 * self.num_days
            df_n = final_df.iloc[i:].reset_index()
            # add another column as x-axis where value is index + 1
            df_n['x'] = df_n.index + 1
            fit = np.polyfit(df_n['x'], np.log(df_n[close_column_name_new]), 1)
            slope.append(fit[0])
            y_fitted = np.exp(fit[1]) * np.exp(fit[0] * df_n['x'])
            r2.append(r2_score(df_n[close_column_name_new], y_fitted))

            trent_flag = int(df_n.iloc[-1][trend_column_name])
            trend.append(trent_flag)
            max_gap_up_percent = float(df_n[percent_chg_col_name].max())
            max_gap_up.append(max_gap_up_percent)

            ticker_atr = df_n[atr_column_name_new].iloc[-1]
            atr.append(ticker_atr)

            daily_risk = account_value * self.risk_factor
            num_stocks_to_buy = math.floor(daily_risk / ticker_atr)
            account_value_allotted = num_stocks_to_buy * df_n[close_column_name_new].iloc[-1]
            position_size = (account_value_allotted / account_value) * 100
            target_percent.append(position_size)

            remaining_cash = remaining_cash - account_value_allotted
            if remaining_cash > 0 and trent_flag == 1 and max_gap_up_percent < 0.15:
                included.append(1)
            else:
                included.append(0)

        sym_param_df = pd.DataFrame()
        sym_param_df['symbol'] = symbols
        sym_param_df['r2'] = r2
        sym_param_df['slope'] = slope
        sym_param_df['trend'] = trend
        sym_param_df['max_gap_up'] = max_gap_up
        sym_param_df['annualised_slope'] = pow(1 + sym_param_df['slope'], 250)
        sym_param_df['mul'] = sym_param_df['r2'] * sym_param_df['annualised_slope']
        sym_param_df['atr'] = atr
        sym_param_df['target_percent'] = target_percent
        sym_param_df['included'] = included

        sym_param_df.sort_values(by=['included', 'mul'], ascending=False, inplace=True)

        print(sym_param_df.head())
        self.save_ranking_results(sym_param_df)
        return sym_param_df

    @staticmethod
    def calculate_atr(data_df, period):
        # Calculate True Range (TR) for each row
        data_df['high-low'] = data_df['high'] - data_df['low']
        data_df['high-previous-close'] = abs(data_df['high'] - data_df['close'].shift(1))
        data_df['low-previous-close'] = abs(data_df['low'] - data_df['close'].shift(1))
        # Calculate the maximum of the three TR values
        data_df['true_range'] = data_df[['high-low', 'high-previous-close', 'low-previous-close']].max(axis=1)
        # Calculate ATR using the rolling mean of the True Range
        data_df['ATR'] = data_df['true_range'].rolling(window=period).mean()
        # Drop the intermediate columns used for TR calculation
        data_df.drop(['high-low', 'high-previous-close', 'low-previous-close', 'true_range'], axis=1, inplace=True)

    def save_ranking_results(self, sym_param_df):
        sym_param_df.to_csv(self.results_dir + self.ranking_file_name, index=False)


class MomentumMeasureStrategy(ABC):
    pass


class ExponentialRegressionMomentumMeasureStrategy(MomentumMeasureStrategy):
    pass
