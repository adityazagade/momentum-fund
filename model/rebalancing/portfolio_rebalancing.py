import datetime
import logging
import math
from abc import ABC, abstractmethod
from model.results import ResultBuilder, Result
from model.market_regime_filter import MarketRegimeFilter
from model.portfolio.portfolio import Portfolio
from model.position_sizing.position_sizing_strategies import PositionSizingStrategy
from model.ranking.ranking_result import RankingTable, RankingTableRow
from model.rebalancing.rebalancing_result import RebalancingResult
from model.scheduling.schedule import Schedule
from services.portfolio_service import PortfolioService


class PortfolioRebalancingStrategy(ABC):
    """ Portfolio Rebalancing is how you change your stock portfolio over time"""

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def rebalance_portfolio(self,
                            portfolio: Portfolio,
                            ranking_table: RankingTable,
                            cash_flow: float) -> RebalancingResult:
        pass


class PortfolioRebalancingStrategyStrategyImpl(PortfolioRebalancingStrategy):
    """ e.g.
    1. We hold a portfolio of 20 stocks and require that the stocks must remain in the top 30
    2. When we do a portfolio rebalance, each stop must be in the top 20% of the universe of stocks or
    if it trades below its 100-day moving average
    """

    def __init__(self,
                 top_n_percent: int,
                 ticker_ema_span: int,
                 market_regime_filter: MarketRegimeFilter,
                 risk_factor: float,
                 position_sizing_strategy: PositionSizingStrategy,
                 position_rebalance_schedule: Schedule,
                 threshold: float) -> None:
        super().__init__()
        self.threshold = threshold
        self.position_sizing_strategy = position_sizing_strategy
        self.portfolio_service = PortfolioService()
        self.risk_factor = risk_factor
        self.top_n_percent = top_n_percent
        self.ticker_ema_span = ticker_ema_span
        self.market_regime_filter = market_regime_filter
        self.position_rebalance_schedule = position_rebalance_schedule
        self.logger = logging.getLogger(__name__)

    def rebalance_portfolio(self,
                            portfolio: Portfolio,
                            ranking_table: RankingTable,
                            cash_flow: float,
                            ) -> RebalancingResult:
        rebalancing_result = RebalancingResult()
        rebalancing_result.portfolio = portfolio

        # create a dictionary of stocks and their last close price
        last_close_data = {}
        for row in ranking_table.rows:
            last_close_data[row.symbol] = row.closing_price

        # Using the ranking table, get the top n% of stocks. e.g. top 20%
        # For each stock in the portfolio, check if it is in the top n% of stocks
        # If it is not, then sell the stock
        stocks_to_sell = []
        top_n_percent_rows = self.get_top_n_percent(ranking_table, self.top_n_percent)
        stocks_in_top_n_percentile = [row.symbol for row in top_n_percent_rows]
        for holding in portfolio.holdings:
            if holding.symbol not in stocks_in_top_n_percentile:
                # closing_price = last_close_data[holding.symbol]
                # closing_price = position_sizing_result.get_last_close(holding.symbol)
                stocks_to_sell.append(holding.symbol)

        for ticker in stocks_to_sell:
            portfolio.sell_stock(ticker, last_close_data[ticker])
            rebalancing_result.add_stocks_to_sell(ticker)

        account_value = portfolio.get_account_value(last_close_data)
        daily_risk = account_value * self.risk_factor
        position_sizing_result = self.position_sizing_strategy.calculate_position_sizes(ranking_table, account_value)

        if self.position_rebalance_schedule.matches(datetime.date.today()):
            # we rebalance positions first
            self.logger.info("Rebalance positions first")
            for holding in portfolio.holdings:
                ticker = holding.symbol
                expected_weight = position_sizing_result.get_weight(ticker)
                current_weight = holding.quantity * last_close_data[ticker] / account_value
                threshold = self.threshold

                # first sell things that are overweight
                if abs(expected_weight - current_weight) > threshold:
                    # rebalance position
                    self.logger.info(f"Rebalancing position for {ticker}")
                    current_atr = position_sizing_result.get_atr(ticker)
                    last_close = position_sizing_result.get_last_close(ticker)
                    expected_num_stocks = math.floor(daily_risk / current_atr)
                    actual_num_stocks = holding.quantity

                    if current_weight > expected_weight:
                        num_stocks_to_sell = actual_num_stocks - expected_num_stocks
                        portfolio.sell_stock(ticker, last_close, num_stocks_to_sell)
                        rebalancing_result.add_stock_to_reduce(ticker,
                                                               num_stocks_to_sell,
                                                               last_close,
                                                               current_weight,
                                                               expected_weight)
                    else:
                        num_stocks_to_buy = expected_num_stocks - actual_num_stocks
                        portfolio.buy_stock(ticker, num_stocks_to_buy, last_close)
                        rebalancing_result.add_stock_to_increase(ticker,
                                                                 num_stocks_to_buy,
                                                                 last_close,
                                                                 current_weight,
                                                                 expected_weight)

        # if cash available after rebalancing positions, then buy new positions
        available_cash = portfolio.cash
        if available_cash <= 0:
            self.logger.info("No cash available. Skip execution")
            return rebalancing_result

        if not self.market_regime_filter.is_allowed():
            self.logger.info("Market regime does not allow any buying. Skip execution")
            return rebalancing_result

        # For each stock in the ranking_table, start from top and check if it is in the portfolio
        # If it is not, then buy the stock
        for row in ranking_table.rows:
            if not portfolio.is_present(row.symbol) and \
                    row.included is True and \
                    available_cash > 0 and \
                    row.symbol not in stocks_to_sell and \
                    row.symbol in stocks_in_top_n_percentile:
                # buy stock
                current_atr = position_sizing_result.get_atr(row.symbol)
                last_close = position_sizing_result.get_last_close(row.symbol)
                num_stocks_to_buy = math.floor(daily_risk / current_atr)
                account_value_allotted = num_stocks_to_buy * last_close
                weight = account_value_allotted / account_value
                available_cash = available_cash - account_value_allotted
                if available_cash < 0:
                    break
                portfolio.buy_stock(row.symbol, num_stocks_to_buy, last_close)
                rebalancing_result.add_stock_to_buy(row.symbol, num_stocks_to_buy, weight)

        result = ResultBuilder() \
            .with_ranking_results(ranking_table) \
            .with_position_sizing_result(position_sizing_result) \
            .build()

        self.print_and_save(result)
        return rebalancing_result

    def print_and_save(self, result: Result):
        self.logger.info(result)
        self.logger.info("Saving results to filesystem")
        result.save()

    @staticmethod
    def get_top_n_percent(ranking_table: RankingTable, top_n_percent: int) -> list[RankingTableRow]:
        total_stocks = len(ranking_table.rows)
        top_n = int(total_stocks * (top_n_percent / 100))
        return ranking_table.rows[:top_n]
