from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token
from channels.auth import AuthMiddlewareStack
from urllib.parse import parse_qs

async def get_user(query_string,headers):
    if b"token" in query_string:
        try:
            token_key = query_string[b"token"][0]
            token_key = token_key.decode()
            token = await Token.objects.select_related('user').aget(key=token_key)
            return token.user
        except:
            return AnonymousUser()
    elif b'authorization' in headers:
        try:
            token_name, token_key = headers[b'authorization'].decode().split()
            if token_name == 'Token':
                token = await Token.objects.select_related('user').aget(key=token_key)
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

def TokenAuthMiddlewareStack(inner): 
    return TokenAuthMiddleware(AuthMiddlewareStack(inner))    