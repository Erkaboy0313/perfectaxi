from django.db import models
from .managers import RoomManager,MessageManager

class Room(models.Model):
    
    class Room_type(models.TextChoices):
        PUBLIC = 'public'
        ADMIN = 'admin'
    
    users = models.ManyToManyField('users.User')
    name = models.CharField(max_length = 255,blank=True, null=True)
    type = models.CharField(max_length = 10,choices = Room_type.choices, default = Room_type.PUBLIC)
    
    
    aobjects = RoomManager()
    objects = models.Manager()
    
    def __str__(self) -> str:
        return self.name        
    
class Message(models.Model):
    author = models.ForeignKey('users.User',on_delete=models.CASCADE)
    room = models.ForeignKey(Room,on_delete = models.CASCADE)
    message = models.TextField()
    
    aobjects = MessageManager()
    objects = models.Manager()
    
    time = models.DateTimeField(auto_now_add = True)
    
        