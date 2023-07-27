from django.db import models
from users.models import Client
# Create your models here.

class Card(models.Model):
    user = models.ForeignKey(Client,on_delete=models.CASCADE)
    cardNumber = models.CharField(max_length=20)
    cardExpireDate = models.CharField(max_length=5)
    cvc = models.CharField(max_length=3)

    def __str__(self):
        return f"{self.cardNumber} {self.user}"