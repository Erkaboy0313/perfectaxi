from django.db.models import Manager,Case,When,F,CharField,Subquery,OuterRef,Value
from django.db.models.functions import Concat
from users.models import User

class RoomManager(Manager):
    
    async def get_chat(self,user1,user2):
        chat = await self.filter(users = user1).filter(users = user2).afirst()
        if not chat:
            name = f"chat-{user1.id}-{user2.id}"
            chat = await self.acreate(name = name)
            await chat.users.aadd(user1)
            await chat.users.aadd(user2)
        return chat
    
    async def load_admin_chats(self):
        # return self.filter(type = 'admin').prefetch_related('users')
        
        admin_rooms = self.filter(type='admin').prefetch_related('users')
        
        non_admin_user_subquery = Subquery(
            User.objects.filter(
                room__id=OuterRef('id'),  # Filter users in the current room
            ).exclude(role=User.UserRole.ADMIN).annotate(full_name=Concat(F('first_name'), Value(' '), F('last_name')))
            .values('full_name')[:1]
        )
        
        return admin_rooms.annotate(non_admin_user_name=non_admin_user_subquery)
    
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
    