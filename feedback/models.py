from django.db import models
from users.models import Client,Driver
# Create your models here.

class Feedback(models.Model):
    client = models.ForeignKey(Client,on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver,on_delete=models.CASCADE)
    mark = models.PositiveIntegerField()
    resons = models.ManyToManyField('Reson')
    time = models.DateField(null=True,blank=True,auto_now_add=True)

class Reson(models.Model):

    class ResonType(models.TextChoices):
        PROBLEM = 'problem'
        COMFORT = 'comfort'

    type = models.CharField(max_length=20,choices=ResonType.choices,null=True)
    icon = models.FileField(upload_to='Problems/')
    name = models.CharField(max_length=100,null=True)

    def __str__(self):
        return self.name
    