from django.db import models
from .managers import CategoryManager

class CarService(models.Model):

    class ServiceChoices(models.TextChoices):
        STANDART = 'standart'
        BUSSINESS = 'bussiness'
        COMFORT = 'comfort'

    service = models.CharField(max_length=100,choices=ServiceChoices.choices,null=True)
    includedCars = models.CharField(max_length=255,null=True)
    start_price = models.IntegerField(default=0)
    price_per_km = models.FloatField(default=0)

    objects = models.Manager()
    filter = CategoryManager()

    def __str__(self):
        return self.service