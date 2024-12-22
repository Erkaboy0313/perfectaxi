from .async_view import lastOrderClient

from asgiref.sync import async_to_sync


def last_order_client(user):
    return async_to_sync(lastOrderClient)(user)


