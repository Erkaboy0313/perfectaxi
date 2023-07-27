from django.db import models


class PricingClient(models.Model):
    price = models.FloatField()

    def __str__(self):
        return f"{self.price}"
    

class PricingDriver(models.Model):
    price = models.FloatField()
    
    def __str__(self):
        return f"{self.price}"

