from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Room,Message
from users.models import User
import json
from .serializers import chat_room_serializer,messages_serializer,message_serializer

class ChatConsumer(AsyncWebsocketConsumer):
    
    @staticmethod
    def isAuthenticatedC(func):
        async def wrapper(self,*args,**kwargs):
            user = self.scope["user"]
            if user.is_authenticated:
                return await func(self,*args,**kwargs)
            else:
                await self.accept()
                await self.send_error({"error_text":"Invalid Token"})
                await self.close()
        return wrapper
    
    @isAuthenticatedC
    async def connect(self):
        await self.accept()
        user = self.scope["user"]
        self.room_name = f"chat_user_{user.id}"
        # Join room group
        await self.channel_layer.group_add(self.room_name, self.channel_name)

    async def disconnect(self, close_code):
        await self.close()
        
    async def fetch_message(self,data):
        user_id = data['receiver_id']
        user1 = self.scope['user']
        user2 = await User.objects.aget(id = int(user_id))
        chat = await Room.aobjects.get_chat(user2,user1)
        messages = await Message.aobjects.retrive_chat_messages(chat)
        data = {
            "command":"fetch_message",
            "chat": await chat_room_serializer(chat),
            "messages":await messages_serializer(messages)
        }
        return await self.send(text_data=json.dumps({"message": data}))
    
    async def new_message(self,data):
        user_id = data['receiver_id']
        user1 = self.scope['user']
        user2 = await User.objects.aget(id = int(user_id))
        chat = await Room.aobjects.get_chat(user2,user1)
        message = await Message.objects.acreate(author = user1,room = chat,message = data['message'])
        data = {
            "command":"new_message",
            "chat": await chat_room_serializer(chat),
            "messages": await message_serializer(message)
        }
        await self.send_receiver(user_id,data)    
        return await self.send(text_data=json.dumps({"message":{"command":"send","status":True}}))
    
    async def contact_admin(self,data):
        user = self.scope['user']
        chat = Room.aobjects.get_chat_with_admin(user)
        messages = await Message.aobjects.retrive_chat_messages(chat)
        data = {
            "command":"fetch_message",
            "chat": await chat_room_serializer(chat),
            "messages":await messages_serializer(messages)
        }
        return await self.send(text_data=json.dumps({"message": data}))
        
    commands = {
        "fetch_message":fetch_message,
        "new_message":new_message,
        "contact with admin":contact_admin
    }
    
    async def send_receiver(self,receiver_id,data):
        await self.channel_layer.group_send(
            f"chat_user_{receiver_id}",
            {
                "type":"chat_message",
                "message":data
            }
        )

    async def send_error(self, message):
        await self.send(text_data=json.dumps(
            {   
                "action":"error",
                'message':message
            }
        )) 

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        return await self.commands[data['command']](self , data)

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))