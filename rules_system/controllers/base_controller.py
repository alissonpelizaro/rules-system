from rules_system.exceptions import MethodNotImplementedException


class BaseController:
    """Base controller class with placeholder methods for CRUD operations.

    This class serves as a base for creating controllers in a web application.
    It provides placeholder methods for common CRUD (Create, Read, Update,
    Delete) operations. Each method raises a MethodNotImplementedException,
    indicating that the specific HTTP method should be implemented in the
    derived controller.

    Args:
        request (object): An optional object representing the incoming request.

    Attributes:
        request (object): The incoming request object associated with the
                         controller instance.

    Example:
        To create a custom controller that extends BaseController:
        >>> class CustomController(BaseController):
        ...     def get(self, _id: str):
        ...         # Custom implementation for handling GET requests
        ...         pass

    Methods:
        - get(_id: str): Placeholder method for handling GET requests.
        - post(): Placeholder method for handling POST requests.
        - put(_id: str): Placeholder method for handling PUT requests.
        - delete(_id: str): Placeholder method for handling DELETE requests.
    """
    
    def __init__(self, request = None) -> None:
        """Initializes the BaseController.

        Args:
            request (object): An optional object representing the incoming request.
        """
        self.request = request
        
    def get(self, _id:str):
        """Placeholder method for handling GET requests.

        Args:
            _id (str): Identifier for the resource.

        Raises:
            MethodNotImplementedException: Indicates that the method should be implemented
                                           in the derived controller.
        """
        raise MethodNotImplementedException('GET')
    
    def post(self):
        """Placeholder method for handling POST requests.

        Raises:
            MethodNotImplementedException: Indicates that the method should be implemented
                                           in the derived controller.
        """
        raise MethodNotImplementedException('POST')
    
    def put(self, _id:str):
        """Placeholder method for handling PUT requests.

        Args:
            _id (str): Identifier for the resource.

        Raises:
            MethodNotImplementedException: Indicates that the method should be implemented
                                           in the derived controller.
        """
        raise MethodNotImplementedException('PUT')
    
    def delete(self, _id:str):
        """Placeholder method for handling DELETE requests.

        Args:
            _id (str): Identifier for the resource.

        Raises:
            MethodNotImplementedException: Indicates that the method should be implemented
                                           in the derived controller.
        """
        raise MethodNotImplementedException('DELETE')