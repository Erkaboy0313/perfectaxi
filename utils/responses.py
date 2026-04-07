from rest_framework.response import Response


def success_response(data=None, status=200):
    return Response({'code': 'success', 'data': data}, status=status)


def error_response(code, error_message, status=400):
    return Response({'code': code, 'error_message': error_message}, status=status)


class SuccessResponseMixin:
    """
    Mixin that wraps all successful (< 400) DRF responses in a standard envelope:
        {"code": "success", "data": <original data>}
    Responses that already have a 'code' key are left untouched.
    """

    def finalize_response(self, request, response, *args, **kwargs):
        if (
            hasattr(response, 'data')
            and response.status_code < 400
            and not (isinstance(response.data, dict) and 'code' in response.data)
        ):
            response.data = {'code': 'success', 'data': response.data}
        return super().finalize_response(request, response, *args, **kwargs)
