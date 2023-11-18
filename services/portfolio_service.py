import logging

import pandas as pd

from clients.nse_client import NSEClient
from services.config_service import ConfigService
from model.portfolio.portfolio import Portfolio

PROPERTIES_FILE = 'app.properties'

PORTFOLIO_FILE_KEY = 'portfolio.file'


class PortfolioService:
    def __init__(self) -> None:
        super().__init__()
        self.config_service = ConfigService.get_instance()
        self.nse_client = NSEClient.get_instance()
        self.logger = logging.getLogger(__name__)

    def get_portfolio(self) -> Portfolio:
        self.logger.info('Fetching portfolio')
        return self.load_from_file()

    def load_from_file(self) -> Portfolio:
        self.logger.info('Loading portfolio from file')
        file = self.config_service.get(PORTFOLIO_FILE_KEY)
        # import csv using pandas
        df = pd.read_csv(file)
        return Portfolio.from_df(df)
