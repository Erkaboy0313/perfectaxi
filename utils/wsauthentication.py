from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from urllib.parse import parse_qs
from rest_framework.authtoken.models import Token


@database_sync_to_async
def get_user(query_string,headers):
    if b"token" in query_string:
        try:
            token_key = query_string[b"token"][0]
            token_key = token_key.decode()
            token = Token.objects.get(key=token_key)
            return token.user
        except:
            return AnonymousUser()
    elif b'authorization' in headers: 
        try:
            token_name, token_key = headers[b'authorization'].decode().split()
            if token_name == 'Token':
                token = Token.objects.get(key=token_key)
                return token.user
        except Token.DoesNotExist:
            return AnonymousUser()
    else:
        return AnonymousUser()

class TokenAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        query_string = parse_qs(
        scope["query_string"]
        )  # used for querystring token url auth
        headers = dict(scope['headers'])
        scope['user'] = await get_user(query_string,headers)
        return await self.inner(scope, receive, send)


class TokenAuthMiddlewareInstance:
    """
    Yeah, this is black magic:
    https://github.com/django/channels/issues/1399
    """

    def __init__(self, scope, middleware):
        self.middleware = middleware
        self.scope = dict(scope)
        self.inner = self.middleware.inner

    async def __call__(self, receive, send):
        query_string = self.scope["query_string"]
    # used for querystring token url auth
        headers = dict(self.scope['headers'])
        self.scope['user'] = await get_user(query_string,headers)
        inner = self.inner(self.scope)
        return await inner(receive, send)


def TokenAuthMiddlewareStack(inner): return TokenAuthMiddleware(
    AuthMiddlewareStack(inner))    