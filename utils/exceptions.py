from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError, NotAuthenticated, PermissionDenied
from rest_framework.response import Response

from utils.error_codes import (
    VALIDATION_ERROR,
    NOT_AUTHENTICATED,
    PERMISSION_DENIED,
    SERVER_ERROR,
)


def custom_exception_handler(exc, context):
    """
    Custom DRF exception handler that returns every error in the standard envelope:
        {"code": "<ERROR_CODE>", "error_message": "<human readable message>"}
    """
    # Let DRF do its default pre-processing (sets response for known exceptions)
    response = exception_handler(exc, context)

    # BaseAPIException – already carries an error_code set in exceptions.py
    from PerfectTaxi.exceptions import BaseAPIException
    if isinstance(exc, BaseAPIException):
        return Response(
            {'code': exc.error_code, 'error_message': str(exc.detail)},
            status=exc.status_code,
        )

    # DRF ValidationError
    if isinstance(exc, ValidationError):
        errors = exc.detail
        if isinstance(errors, dict):
            first_field = next(iter(errors))
            first_error = errors[first_field]
            message = str(first_error[0]) if isinstance(first_error, list) else str(first_error)
        elif isinstance(errors, list):
            message = str(errors[0])
        else:
            message = str(errors)
        return Response(
            {'code': VALIDATION_ERROR, 'error_message': message},
            status=400,
        )

    # DRF NotAuthenticated (401)
    if isinstance(exc, NotAuthenticated):
        return Response(
            {'code': NOT_AUTHENTICATED, 'error_message': 'Authentication credentials were not provided'},
            status=401,
        )

    # DRF PermissionDenied (403)
    if isinstance(exc, PermissionDenied):
        return Response(
            {'code': PERMISSION_DENIED, 'error_message': 'You do not have permission to perform this action'},
            status=403,
        )

    # For any other exception that DRF recognised, keep DRF's response as-is
    if response is not None:
        return response

    # Truly unhandled exception
    return Response(
        {'code': SERVER_ERROR, 'error_message': 'An unexpected error occurred'},
        status=500,
    )
