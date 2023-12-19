class InvalidFilterException(Exception):
    """Exception class raised when the type of a Rule filter is not a list
    """
    def __init__(self, message = None) -> None:
        self.message = message if message else f"Rule filter must be List type"
        super().__init__(self.message)
        

class InvalidFilterOperationException(InvalidFilterException):
    """Exception class raised when an invalid operation condition is defined
    """
    def __init__(self, operation_list):
        message = f"Rule filter must have an 'operation' field with one of this values: { (', ').join(operation_list) }."
        self.message = message
        super().__init__(self.message)
        

class RuleFilterOperationMissingFieldException(InvalidFilterException):
    """Exception class raised for rules with a missing mandatory field
    """
    def __init__(self, operation, field):
        message = f"Field '{field}' is mandatory for '{operation}' condition in a rule filter."
        self.message = message
        super().__init__(self.message)
        

class MissingRuleKeyException(InvalidFilterException):
    """Exception class raised for rules whitout a 'key' field
    """
    def __init__(self):
        message = f"Rule filter must have a 'key' field."
        self.message = message
        super().__init__(self.message)
        