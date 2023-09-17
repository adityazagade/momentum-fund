import logging

from clients.nse_client import NSEClient
from config.app_config import AppConfig

APP_PROPERTIES = 'app.properties'


class IndexDataService:
    def __init__(self) -> None:
        super().__init__()
        self.app_config = AppConfig(APP_PROPERTIES)
        self.logger = logging.getLogger(__name__)
        self.nse_client = NSEClient()

    def get_index_constituents(self, index: str):
        self.logger.info(f'Getting index constituents for index: {index}')
        stock_universe = self.nse_client.get_stock_universe(index)
        stock_universe.remove('PATANJALI')  # Some issue with this stock
        # return stock_universe[-20:]
        return stock_universe
        # return ['JBMA']
