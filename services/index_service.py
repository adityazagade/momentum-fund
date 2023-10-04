"""
This module contains IndexDataService class which is responsible for fetching index related data
"""

import logging

from clients.nse_client import NSEClient
from config.app_config import AppConfig
from model.company_info import CompanyInfo
from model.filter.filters import IndexConstituentsFilter

APP_PROPERTIES = 'app.properties'


class IndexDataService:
    """
    This service class is responsible for fetching index related data
    """

    def __init__(self) -> None:
        super().__init__()
        self.app_config = AppConfig(APP_PROPERTIES)
        self.logger = logging.getLogger(__name__)
        self.nse_client = NSEClient.get_instance()

    def get_index_constituents(self,
                               index: str,
                               index_filter: IndexConstituentsFilter = None):
        """
        This method fetches index constituents for a given index
        :param index_filter: filter criteria for index constituents
        :param index: index_name (e.g. NIFTY 50)
        :return: list of stocks in the index
        """
        self.logger.info("Getting index constituents for index: %s", index)
        stock_universe = self.nse_client.get_stock_universe(index)
        # if PATANJALI is present in stock_universe, remove it
        if 'PATANJALI' in stock_universe:
            stock_universe.remove('PATANJALI')  # Some issue with this stock
        # stock_universe =  stock_universe[-5:]
        # stock_universe.append('SBIN')
        filtered_stock_universe = stock_universe
        if index_filter:
            company_info_list = self.get_company_info(stock_universe)
            if index_filter.min_market_cap:
                filtered_stock_universe = [company_info.symbol for company_info in company_info_list if
                                           company_info.market_cap >= index_filter.min_market_cap]
            if index_filter.max_market_cap:
                filtered_stock_universe = [company_info.symbol for company_info in company_info_list if
                                           company_info.market_cap <= index_filter.max_market_cap]
        return filtered_stock_universe
        # return ['JBMA']

    def get_company_info(self, stock_universe: list[str]) -> list[CompanyInfo]:
        """
        This method fetches company info for a given stock universe
        :param stock_universe: list of stocks to fetch company info for
        :return: list of company info
        """
        company_info_list = []
        for ticker in stock_universe:
            company_info = self.nse_client.try_to_get_company_info(ticker)
            company_info_list.append(company_info)
        return company_info_list
