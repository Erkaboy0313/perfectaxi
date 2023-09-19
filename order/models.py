from django.db import models
from users.models import Client,Driver
from .managers import SeriviseManger
# Create your models here.

class Order(models.Model):

    class OrderStatus(models.TextChoices):
        ACTIVE = 'active'
        DELIVERING = 'delivering'
        DELIVERED = 'delivered'
        REJECTED = 'rejected'

    client = models.ForeignKey(Client,on_delete=models.CASCADE, null=True,blank=True)
    driver = models.ForeignKey(Driver,on_delete=models.CASCADE,null=True,blank=True)
    carservice = models.ForeignKey('category.CarService',on_delete=models.CASCADE,null=True,blank=True)
    contact_number = models.CharField(max_length=35, null=True,blank=True)
    start_adress = models.CharField(max_length=255, null=True,blank=True)
    start_point = models.CharField(max_length=40, null=True,blank=True)
    ordered_time = models.DateTimeField(auto_now_add=True,blank=True)
    taken_time = models.DateTimeField(null=True,blank=True)
    complated_time = models.DateTimeField(null=True,blank=True)
    rejected_time = models.DateTimeField(null=True,blank=True)
    distance = models.FloatField(null=True,blank=True)
    price = models.FloatField(null=True,blank=True)
    payment_type = models.CharField(max_length=4,null=True,blank=True)
    status = models.CharField(max_length=15,choices=OrderStatus.choices,default=OrderStatus.ACTIVE,blank=True)
    reject_reason = models.TextField(null=True,blank=True)
    services = models.ManyToManyField('Services',blank=True)

    def __str__(self):
        return f"{self.client} - {self.driver} - {self.ordered_time} - {self.status}"
    
    def save(self, *args, **kwargs):
        if not self.contact_number:
            self.contact_number = self.client.user.phone
        self.payment_type = self.client.payment_type
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ['-id']

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

    objects = models.Manager()
    filter = SeriviseManger()

    class Meta:
        verbose_name_plural = 'Services'

    def __str__(self):
        return f"{self.name} - {self.cost}"