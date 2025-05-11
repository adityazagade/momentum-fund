"""
This module provides services for managing and interacting with portfolios.
"""

import logging

import pandas as pd

from clients.nse_client import NSEClient
from services.config_service import ConfigService
from model.portfolio.portfolio import Portfolio

PROPERTIES_FILE = 'app.properties'

PORTFOLIO_FILE_KEY = 'portfolio.file'


class PortfolioService:
    """
    This service class is responsible for managing portfolio operations.
    """

    def __init__(self) -> None:
        """
        Initializes the PortfolioService with necessary configurations and clients.
        """
        super().__init__()
        self.config_service = ConfigService.get_instance()
        self.nse_client = NSEClient.get_instance()
        self.logger = logging.getLogger(__name__)

    def get_portfolio(self) -> Portfolio:
        """
        Fetches the portfolio by loading it from a file.
        
        :return: Portfolio object
        """
        self.logger.info('Fetching portfolio')
        return self.load_from_file()

    def load_from_file(self) -> Portfolio:
        """
        Loads the portfolio from a file specified in the configuration.
        
        :return: Portfolio object
        """
        self.logger.info('Loading portfolio from file')
        file = self.config_service.get(PORTFOLIO_FILE_KEY)
        # import csv using pandas
        data_frame = pd.read_csv(file)
        return Portfolio.from_df(data_frame)
