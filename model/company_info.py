"""
CompanyInfo class
"""


class CompanyInfo:
    """
    This class represents company info
    """

    def __init__(self, ticker: str, market_cap: float, free_float_market_cap: float) -> None:
        """
        This method initializes CompanyInfo object
        :param ticker: ticker symbol
        :param market_cap: market cap
        :param free_float_market_cap: free float market cap
        """
        super().__init__()
        self.symbol: str = ticker
        self.market_cap: float = market_cap
        self.free_float_market_cap: float = free_float_market_cap

    @classmethod
    def from_json(cls, ticker: str, json_result: dict):
        """
        This method creates CompanyInfo object from json
        :param ticker: ticker symbol
        :param json_result:  result
        :return: CompanyInfo object
        """
        # It is possible that either of these keys are not present in the json. In that case, set market_cap to 0
        trade_info = json_result.get('marketDeptOrderBook', {}).get('tradeInfo', {})
        total_market_cap = trade_info.get('totalMarketCap', 0)
        ffmc = trade_info.get('ffmc', 0)
        return cls(
            ticker=ticker,
            market_cap=total_market_cap,
            free_float_market_cap=ffmc
        )
