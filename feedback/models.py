from django.db import models
from order.models import Order
# Create your models here.

class Feedback(models.Model):
    
    class FeedBackType(models.TextChoices):
        CLIENT = 'client'
        DRIVER = 'driver'
    
    order = models.ForeignKey(Order,on_delete=models.CASCADE,null=True)
    type = models.CharField(max_length = 20, choices = FeedBackType.choices, default = FeedBackType.CLIENT)
    mark = models.PositiveIntegerField()
    resons = models.ManyToManyField('Reson',blank=True)
    time = models.DateField(null=True,blank=True,auto_now_add=True)

    class Meta:
        ordering = ['-time']

class Reson(models.Model):

    class ResonType(models.TextChoices):
        PROBLEM = 'problem'
        COMFORT = 'comfort'

    type = models.CharField(max_length=20,choices=ResonType.choices,null=True)
    icon = models.FileField(upload_to='Problems/')
    name = models.CharField(max_length=100,null=True)

    def __str__(self):
        return self.name
    