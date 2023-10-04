class NSEClientException(Exception):
    """
    This class represents an exception thrown by NSEClient
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)
