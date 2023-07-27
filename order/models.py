from django.db import models
from users.models import Client,Driver
# Create your models here.

class Order(models.Model):

    class OrderStatus(models.TextChoices):
        ACTIVE = 'active'
        DELIVERING = 'delivering'
        DELIVERED = 'delivered'
        REJECTED = 'rejected'

    client = models.ForeignKey(Client,on_delete=models.CASCADE, null=True)
    driver = models.ForeignKey(Driver,on_delete=models.CASCADE,null=True)
    contact_number = models.CharField(max_length=35, null=True)
    start_adress = models.CharField(max_length=255, null=True)
    start_point = models.CharField(max_length=40, null=True)
    ordered_time = models.DateTimeField(auto_now_add=True)
    taken_time = models.DateTimeField(null=True)
    rejected_time = models.DateTimeField(null=True)
    distance = models.FloatField()
    price = models.FloatField()
    payment_type = models.CharField(max_length=4,null=True)
    status = models.CharField(max_length=15,choices=OrderStatus.choices)
    reject_reason = models.TextField(null=True)
    services = models.ManyToManyField('Services')

    def __str__(self):
        return f"{self.client} - {self.driver} - {self.ordered_time} - {self.status}"
    

    class Meta:
        ordering = ['id']

class Point(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    point = models.CharField(max_length=40, null=True)

    def __str__(self):
        return f"{self.order.id} - {self.point}"

    class Meta:
        ordering = ['id']

class Services(models.Model):
    name = models.CharField(max_length=100,null=True)
    cost = models.FloatField()

    def __str__(self):
        return f"{self.name} - {self.cost}"