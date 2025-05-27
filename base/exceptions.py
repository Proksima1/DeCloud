def flatten(exc: BaseException) -> str:
    """
    Will convert exc to flatten string version of exception with all nested exceptions
    """
    str_ = ""
    while True:
        str_ += repr(exc)
        if exc is None or exc.__context__ is None:
            return str_

        exc = exc.__context__
        str_ += " caused by: "


class ServiceError(Exception):
    # General class, for custom exceptions
    ...


class ClientError(ServiceError):
    # This exception is caused by client wrong input, request or actions
    ...


class SupplierError(ServiceError):
    # Something went wrong in supplier
    ...
