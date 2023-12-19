class InvalidActionTypeException(Exception):
    """Exception class raised when an invalid action type is setted
    """

    def __init__(self, action_list: list) -> None:
        self.message = f"Action type must be one of: {(', ').join(action_list)}"
        super().__init__(self.message)