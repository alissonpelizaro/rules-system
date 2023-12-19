from chalice import Response

def response(_return:tuple) -> Response:
    """Generates a Chalice Response object based on the given tuple.

    This function creates a Chalice Response object with the provided tuple.
    The tuple should contain the response body as its first element and an
    optional HTTP status code as its second element. If no status code is
    provided, the default is set to 200 (OK).

    Args:
        _return (tuple): A tuple containing the response body and an optional
                        HTTP status code.

    Returns:
        Response: Chalice Response object.

    Example:
        A successful response with a custom message:
        >>> success_response = response(("Success message", 200))

        An error response with a specific status code and error details:
        >>> error_response = response(("Error details", 400))
    """
    _code = 200
    if type(_return) == tuple and len(_return) > 1:
        _code = _return[1]
    else:
        _return = [_return]
        
    return Response(
        body=_return[0] if _code in [200,201] else {"error": _return[0]},
        headers={'Content-Type': 'application/json'},
        status_code=_code
    )