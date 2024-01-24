from django.db.models import Manager


class RoomManager(Manager):
    
    async def get_chat(self,user1,user2):
        chat = await self.filter(users = user1).filter(users = user2).afirst()
        if not chat:
            name = f"chat-{user1.id}-{user2.id}"
            chat = await self.acreate(name = name)
            await chat.users.aadd(user1)
            await chat.users.aadd(user2)
        return chat
    
    async def get_chat_with_admin(self,client):
        chat = await self.filter(users = client,type = 'admin').afirst()
        if not chat:
            name = f"user_admin_chat_{client.id}"
            chat = await self.acreate(name = name,type = 'admin')
            await chat.users.aadd(client)
        return chat
    
class MessageManager(Manager):
    
    async def retrive_chat_messages(self,chat):
        messages = self.filter(room = chat).select_related('author')
        return messages
    