from django.db import models


class AdminChatRoom(models.Model):

    users = models.ManyToManyField('users.User')
    title = models.CharField(max_length=200)
    closed = models.BooleanField(default=False)

    objects = models.Manager()
    
    @property
    def user_phone(self):
        driver = self.users.filter(role = "driver").first()
        if driver:
            return driver.phone
        else:
            return ''
    
    def __str__(self) -> str:
        return self.name
    
    class Meta:
        ordering = ['closed']
    
class Message(models.Model):
    author = models.ForeignKey('users.User',on_delete=models.CASCADE,related_name='admin_messages')
    room = models.ForeignKey(AdminChatRoom,on_delete = models.CASCADE)
    message = models.TextField()
    seen = models.BooleanField(default=False)
    
    objects = models.Manager()
    
    time = models.DateTimeField(auto_now_add = True)
    
        