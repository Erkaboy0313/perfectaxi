from django.db import models
from users.models import Driver
from order.models import Order
from random import randint

# Create your models here.

class Payment(models.Model):

    class PaymentOperators(models.TextChoices):
        CLICK = 'Click'
        PAYME = 'PAYME'
    
    class PaymentStatus(models.TextChoices):
        WAITING = "waiting"
        PREAUTH = "preauth"
        CONFIRMED = "confirmed"
        REJECTED = "rejected"
        REFUNDED = "refunded"
        ERROR = "error"
        INPUT = "input"

    _id = models.CharField(max_length=255, null=True, blank=False)
    transaction_id = models.CharField(max_length=255, null=True, blank=False)
    balance_id = models.BigIntegerField(null=True, blank=True)
    amount = models.FloatField(null=True, blank=True)
    time = models.BigIntegerField(null=True, blank=True)
    perform_time = models.BigIntegerField(null=True, default=0)
    cancel_time = models.BigIntegerField(null=True, default=0)
    status = models.CharField(max_length=30,null=True, choices=PaymentStatus.choices)
    reason = models.CharField(max_length=255, null=True, blank=True)
    created_at_ms = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payment_operator = models.CharField(max_length=30,choices=PaymentOperators.choices,null=True,blank=True)
    
    def __str__(self):
        return str(self._id)

class Balance(models.Model):
    id_number = models.IntegerField()
    driver = models.OneToOneField(Driver,on_delete=models.SET_NULL,null=True)
    fund = models.FloatField(default=0,blank=True)

    def save(self,*args,**kwargs):
        if not self.id_number:
            while True:
                id = randint(100_000,999_999)
                try:
                    Balance.objects.get(id_number = id)
                except:
                    self.id_number = id
                    break
        return super().save(*args,**kwargs)

    def __str__(self):
        return f"{self.id_number} | {self.fund}"

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