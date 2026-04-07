from rest_framework.exceptions import APIException
from utils.error_codes import SERVER_ERROR


class BaseAPIException(APIException):
    status_code = 400
    default_detail = 'An error occurred'
    default_code = SERVER_ERROR

    def __init__(self, detail=None, code=None):
        self.error_code = code or self.default_code
        super().__init__(detail=detail)