from django.db import models
from users.models import Client,Driver
from .managers import SeriviseManger,DriverHistoryManager
from django.utils import timezone
# Create your models here.

class Order(models.Model):

    class OrderStatus(models.TextChoices):
        ACTIVE = 'active'
        INACTIVE = 'inactive'
        
        ASSIGNED = 'assigned'
        ARRIVED = 'arrived'
        
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
    arived_time = models.DateTimeField(null=True,blank=True)
    started_time = models.DateTimeField(null=True,blank=True)
    complated_time = models.DateTimeField(null=True,blank=True)
    rejected_time = models.DateTimeField(null=True,blank=True)
    distance = models.FloatField(null=True,blank=True)
    price = models.FloatField(null=True,blank=True)
    payment_type = models.CharField(max_length=4,null=True,blank=True)
    status = models.CharField(max_length=15,choices=OrderStatus.choices,default=OrderStatus.ACTIVE,blank=True)
    reject_reason = models.ForeignKey('RejectReason',on_delete=models.SET_NULL,null=True)
    reject_comment = models.TextField(null=True,blank=True)
    services = models.ManyToManyField('Services',blank=True)

    def __str__(self):
        return f"{self.client} - {self.driver} - {self.ordered_time} - {self.status}"
    
    @property 
    def category(self):
        return self.carservice.service
    
    @property
    def service(self):
        return [x.name for x in self.services.all()]
    
    @property
    def client_name(self):
        return self.client.user.name

    async def asave(self, *args, **kwargs):
        time = timezone.now()
        if 'finish' in kwargs:
            del kwargs['finish']
            self.complated_time = time
            wait_time = (self.started_time - self.arived_time).total_seconds() / 60
            if int(wait_time) > 3:
                self.price += int(wait_time - 3) * 500
        if "arrive" in kwargs:
            del kwargs['arrive']
            self.arived_time = time
        if "start" in kwargs:
            del kwargs['start']
            self.started_time = time
        if "reject" in kwargs:
            del kwargs['reject']
            self.rejected_time = time
        
        if not self.contact_number and not self.payment_type:
            self.contact_number = self.client.user.phone
            self.payment_type = self.client.payment_type
        return await super().asave(*args, **kwargs)

    class Meta:
        ordering = ['-id']

class DriverOrderHistory(models.Model):
    
    class OrderStatus(models.TextChoices):
        
        DELIVERING = 'delivering'
        DELIVERED = 'delivered'
        REJECTED = 'rejected'
    
    driver = models.ForeignKey(Driver,on_delete = models.CASCADE)
    order = models.ForeignKey(Order,on_delete = models.CASCADE)
    time = models.DateTimeField(auto_now_add = True)
    status = models.CharField(max_length = 20,choices = OrderStatus.choices)

    objects = models.Manager()
    report = DriverHistoryManager()

class Point(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    point_number = models.IntegerField(null = True)
    point_address = models.CharField(max_length = 255, null=True, blank=True)
    point = models.CharField(max_length=40, null=True)

    def __str__(self):
        return f"{self.order.id} - {self.point}"

    class Meta:
        ordering = ['id']

class RejectReason(models.Model):
    name = models.CharField(max_length = 40)
    
    def __str__(self):
        return self.name

class Services(models.Model):
    name = models.CharField(max_length=100,null=True)
    cost = models.FloatField()

    objects = models.Manager()
    filter = SeriviseManger()

    class Meta:
        verbose_name_plural = 'Services'

    def __str__(self):
        return f"{self.name} - {self.cost}"