from rest_framework.exceptions import APIException


class BaseAPIException(APIException):
    status_code = 400
    default_detail = 'fail_perform'
    default_code = 'error'