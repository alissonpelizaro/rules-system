class MethodNotImplementedException(Exception):
    """Exception class raised when a non implemented controller method is called
    """

    def __init__(self, method: str) -> None:
        self.message = f"Method '{method}' wasn't implemented."
        super().__init__(self.message)