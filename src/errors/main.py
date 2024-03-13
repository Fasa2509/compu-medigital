from enum import Enum

from src.custom_types.Api import ApiResponse


class LocalExceptions(Enum):
    CustomException = "CustomException"
    ConnectionException = "ConnectionException"
    DbException = "DbException"
    ParsingException = "ParsingException"
    AuthException = "AuthException"
    ValidationException = "ValidationException"


EXCEPTION_NAMES = {
    "CustomException": "CustomException",
    "ConnectionException": "ConnectionException",
    "DbException": "DbException",
    "ParsingException": "ParsingException",
    "AuthException": "AuthException",
    "ValidationException": "ValidationException",
}


class CustomException(Exception):
    def __init__(self, message: list[str], errorCode: int = 400, *args: object):
        super().__init__(*args)
        self.message = message
        self.errorCode = errorCode
        self.name = LocalExceptions.CustomException


class ConnectionException(CustomException):
    def __init__(self, message: list[str], errorCode: int = 400, *args: object):
        super().__init__(message, errorCode, *args)
        self.name = LocalExceptions.ConnectionException


class DbException(CustomException):
    def __init__(self, message: list[str], errorCode: int = 400, *args: object):
        super().__init__(message, errorCode, *args)
        self.name = LocalExceptions.DbException


class ParsingException(CustomException):
    def __init__(self, message: list[str], errorCode: int = 400, *args: object):
        super().__init__(message, errorCode, *args)
        self.name = LocalExceptions.ParsingException


class AuthException(CustomException):
    def __init__(self, message: list[str], errorCode: int = 400, *args: object):
        super().__init__(message, errorCode, *args)
        self.name = LocalExceptions.AuthException


class ValidationException(CustomException):
    def __init__(self, message: list[str], errorCode: int = 400, *args: object):
        super().__init__(message, errorCode, *args)
        self.name = LocalExceptions.ValidationException


def ApiErrorHandler(err: Exception, defaultMessage) -> ApiResponse:

    print(err)

    if isinstance(err, CustomException):
        return ApiResponse(error=True, message=err.message)

    return ApiResponse(error=True, message=[defaultMessage])
