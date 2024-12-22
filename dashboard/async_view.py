from chat.models import Room,Message
from .async_serializer import serialize_chats


async def load_admin_chats():
    return await serialize_chats(await Room.aobjects.load_admin_chats())

