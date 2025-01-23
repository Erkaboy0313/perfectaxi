from django.db import models
from .managers import CategoryManager

class CarService(models.Model):

    class ServiceChoices(models.TextChoices):
        STANDART = 'standart'
        BUSSINESS = 'bussiness'
        COMFORT = 'comfort'

    service = models.CharField(max_length=100,choices=ServiceChoices.choices,null=True)
    includedCars = models.CharField(max_length = 255,null = True)
    start_price = models.IntegerField(default = 0)
    price_per_km = models.FloatField(default = 0)
    price_per_min = models.FloatField(default = 0)
    wait_price_per_min = models.FloatField(default = 0)
    free_wait_time = models.IntegerField(default = 0)
    

    objects = models.Manager()
    filter = CategoryManager()

    def __str__(self):
        return self.service
    
class SavedLocation(models.Model):
    user = models.ForeignKey('users.Client',on_delete=models.CASCADE,blank=True,null=True)
    name = models.CharField(max_length=100,blank=True,null=True)
    address = models.CharField(max_length=255,blank=True,null=True)
    point = models.CharField(max_length=40,blank=True,null=True)


    def __str__(self):
        return f"{self.name} | {self.user}"

class CarBrend(models.Model):
    name = models.CharField(max_length=100,blank=True, null=True)

    def __str__(self):
        return self.name

class Color(models.Model):
    name = models.CharField(max_length=100,blank=True, null=True)

    def __str__(self):
        return self.name

class CarModel(models.Model):
    brend = models.ForeignKey(CarBrend,on_delete=models.CASCADE,blank=True,null=True)
    name = models.CharField(max_length=100,blank=True, null=True)

    def __str__(self):
        return self.name