from rest_framework.exceptions import APIException
from rest_framework import status


class BaseCustomException(APIException):
    detail = None
    status_code = None

    def __init__(self, detail, code):
        super().__init__(detail, code)
        self.detail = detail
        self.status_code = code


class UpdateException(BaseCustomException):
    def __init__(self, detail=""):
        super().__init__(detail, status.HTTP_400_BAD_REQUEST)


class ValidationException(BaseCustomException):
    def __init__(self, detail=""):
        super().__init__(detail, status.HTTP_400_BAD_REQUEST)


class BusinessException(BaseCustomException):
    def __init__(self, detail=""):
        super().__init__(detail, status.HTTP_405_METHOD_NOT_ALLOWED)


class ForbiddenException(BaseCustomException):
    def __init__(self, detail=""):
        super().__init__(detail, status.HTTP_403_FORBIDDEN)


class FailedToGenerateReportException(BaseCustomException):
    def __init__(self, detail=""):
        super().__init__(detail, status.HTTP_400_BAD_REQUEST)


class WrongMailCredentialsException(BaseCustomException):
    def __init__(self, detail=""):
        super().__init__(detail, status.HTTP_400_BAD_REQUEST)


class NotFoundException(BaseCustomException):
    def __init__(self, detail=""):
        super().__init__(detail, status.HTTP_404_NOT_FOUND)


class ServerErrorException(BaseCustomException):
    def __init__(self, detail=""):
        super().__init__(detail, status.HTTP_503_SERVICE_UNAVAILABLE)
