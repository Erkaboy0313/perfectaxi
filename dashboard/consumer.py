from channels.generic.websocket import AsyncWebsocketConsumer
import json
# from .decorators import is_admin


class AdminConsumer(AsyncWebsocketConsumer):

    def is_admin(func):
        async def wrapper(self,*args,**kwargs):
            user = self.scope['user']
            if user.is_authenticated:
                if await user.ais_admin():
                    print("worked")
                    return await func(self,*args,**kwargs)
            print("not worked")
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

    commands = {

    }

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.commands[data['command']](self, data)  # Call async commands directly

    async def chat_message(self,data:dict,action:str = None):
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
