from django.db import models
from users.models import Driver,Client

class Notification(models.Model):

    class NotificationType(models.TextChoices):
        DRIVER = 'driver'
        CLIENT = 'client'
        ALL = "all"
        PERSONAL = 'personal'

    client = models.ForeignKey(Client,on_delete=models.CASCADE,null=True)
    driver = models.ForeignKey(Driver,on_delete=models.CASCADE,null=True)
    type = models.CharField(max_length=20,choices=NotificationType.choices)
    message = models.TextField()
    time = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.message} {self.time}"
    
class News(models.Model):
    
    class Receiver(models.TextChoices):
        DRIVER = 'driver'
        CLIENT = 'client'

    receiver = models.CharField(max_length=20,choices=Receiver.choices)
    message = models.TextField()
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.message[:50]} {self.receiver}"

class TermsAndConditions(models.Model):

    text = models.TextField()
    file = models.FileField(upload_to='TermsAndConditions/')

    time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.time
