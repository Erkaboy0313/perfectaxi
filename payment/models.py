from django.db import models
from users.models import Driver
from order.models import Order

# Create your models here.

class Balance(models.Model):
    driver = models.OneToOneField(Driver,on_delete=models.SET_NULL,null=True)
    id = models.IntegerField()
    fund = models.FloatField()

    def __str__(self):
        return f"{self.driver} {self.fund}"

class Payment(models.Model):
    pass

class Charge(models.Model):

    class ChargeStatus(models.TextChoices):
        SUCCESS = 'success'
        FAILED = 'failed'
        REFUNDED = 'refunded'

    balance = models.ForeignKey(Balance,on_delete=models.CASCADE)
    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    charged_fund = models.FloatField()
    charged_time = models.DateTimeField(auto_now_add=True)
    refunded_time = models.DateTimeField(null=True)
    status = models.CharField(max_length=15,choices=ChargeStatus.choices)

    def __str__(self):
        return f"{self.charged_fund} {self.status}"