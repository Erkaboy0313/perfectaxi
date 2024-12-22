from channels.generic.websocket import AsyncWebsocketConsumer
import json
from users.models import User
from chat.models import Message,Room
from chat.serializers import messages_serializer,chat_room_serializer
from .async_view import load_admin_chats
# from .decorators import is_admin


class AdminConsumer(AsyncWebsocketConsumer):

    def is_admin(func):
        async def wrapper(self,*args,**kwargs):
            user = self.scope['user']
            if user.is_authenticated:
                if await user.ais_admin():
                    return await func(self,*args,**kwargs)
            await self.accept()
            await self.chat_message({'data':"User has no privilages"},'error')
        return wrapper
    
    @is_admin
    async def connect(self):

        self.room_group_name = "admin_chat"

        # Accept the connection
        await self.accept()
        await self.join_room(self.room_group_name)
        user = self.scope['user']
        await self.chat_message({"data":'this is how should work'},'default')
        
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )
        
    async def fetch_message(self,data):
        room_name = data['room_name']
        chat = await Room.objects.aget(name = room_name)
        messages = await Message.aobjects.retrive_chat_messages(chat)
        data = {
            "chat": await chat_room_serializer(chat),
            "messages":await messages_serializer(messages)
        }
        return await self.chat_message(data=data,action='fetch_messages')
      
    async def fech_chats(self, data):
        chats = await load_admin_chats()
        return await self.chat_message(chats,'chats')

    commands = {
        "fetch_chat":fech_chats,
        "fetch_message":fetch_message,
    }

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.commands[data['command']](self, data)  # Call async commands directly

    async def chat_message(self,data,action:str = None):
        action = action if action else 'admin_message'
        await self.send(
            text_data=json.dumps({
                'action':action,
                'message':data
            })
        )

    # join room
    async def join_room(self, *args):
        for room_name in args:
            print(f"user joined -> {room_name}")
            await self.channel_layer.group_add(  # Direct async call
                room_name,
                self.channel_name
            )
