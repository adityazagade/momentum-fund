class IndexConstituentsFilter:
    """
    This class represents a filter for index constituents
    """

    def __init__(self,
                 min_market_cap: float = None,
                 max_market_cap: float = None) -> None:
        super().__init__()
        self.min_market_cap: float = min_market_cap
        self.max_market_cap: float = max_market_cap
