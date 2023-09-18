import logging
import math
from abc import ABC, abstractmethod

from model.market_regime_filter import MarketRegimeFilter
from model.portfolio.portfolio import Portfolio
from model.position_sizing.position_sizing_result import PositionSizingResult
from model.ranking.ranking_result import RankingTable, RankingTableRow
from model.rebalancing.rebalancing_result import RebalancingResult
from services.portfolio_service import PortfolioService


class PortfolioRebalancingStrategy(ABC):
    """ Portfolio Rebalancing is how you change your stock portfolio over time"""

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def rebalance_portfolio(self,
                            portfolio: Portfolio,
                            ranking_table: RankingTable,
                            position_sizing_result: PositionSizingResult) -> RebalancingResult:
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
                 risk_factor: float) -> None:
        super().__init__()
        self.portfolio_service = PortfolioService()
        self.risk_factor = risk_factor
        self.top_n_percent = top_n_percent
        self.ticker_ema_span = ticker_ema_span
        self.market_regime_filter = market_regime_filter
        self.logger = logging.getLogger(__name__)

    def rebalance_portfolio(self,
                            portfolio: Portfolio,
                            ranking_table: RankingTable,
                            position_sizing_result: PositionSizingResult) -> RebalancingResult:
        rebalancing_result = RebalancingResult()
        rebalancing_result.portfolio = portfolio
        # Using the ranking table, get the top n% of stocks. e.g. top 20%
        # For each stock in the portfolio, check if it is in the top n% of stocks
        # If it is not, then sell the stock
        stocks_to_sell = []
        filtered_rows = self.get_top_n_percent(ranking_table, self.top_n_percent)
        stocks_in_top_n_percentile = [row.symbol for row in filtered_rows]
        for holding in portfolio.holdings:
            if holding.symbol not in stocks_in_top_n_percentile:
                closing_price = position_sizing_result.get_last_close(holding.symbol)
                portfolio.sell_stock(holding.symbol, closing_price)
                stocks_to_sell.append(holding.symbol)

        rebalancing_result.stocks_to_sell = stocks_to_sell

        if not self.market_regime_filter.is_allowed():
            self.logger.info("Market regime does not allow any buying. Skip execution")
            return rebalancing_result

        # create a dictionary of stocks and their last close price
        last_close_data = {}
        for row in ranking_table.rows:
            last_close_data[row.symbol] = row.closing_price

        account_value = portfolio.get_account_value(last_close_data)
        available_cash = portfolio.cash
        daily_risk = account_value * self.risk_factor
        # For each stock in the ranking_table, start from top and check if it is in the portfolio
        # If it is not, then buy the stock
        for row in ranking_table.rows:
            if not portfolio.is_present(row.symbol) and row.included == 1 and available_cash > 0:
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
        return rebalancing_result

    def get_top_n_percent(self, ranking_table: RankingTable, top_n_percent: int) -> list[RankingTableRow]:
        total_stocks = len(ranking_table.rows)
        top_n = int(total_stocks * (top_n_percent / 100))
        return ranking_table.rows[:top_n]
