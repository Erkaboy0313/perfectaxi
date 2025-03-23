from django.db import models
from parler.models import TranslatableModel,TranslatedFields


class AppLinks(models.Model):
    play_market = models.URLField()
    app_store = models.URLField()
    
    def __str__(self):
        return self.play_market


class Service(TranslatableModel):
    translations = TranslatedFields(
        name = models.CharField(max_length=100),
        title = models.TextField(),
        text = models.TextField()
    )


class Pricing(TranslatableModel):
    translations = TranslatedFields(
        name = models.CharField(max_length=100)
    )
    service = models.ForeignKey(Service,on_delete=models.CASCADE,related_name="prices")
    cost = models.FloatField(default=0)
    
    def __str__(self):
        return self.safe_translation_getter('name')

class Statistic(TranslatableModel):
    translations = TranslatedFields(
        text = models.TextField()
    )
    avilable_drivers = models.IntegerField()
    clients = models.IntegerField()
    drivers = models.IntegerField()
    rides = models.IntegerField()

    def __str__(self):
        return f"{self.avilable_drivers} - {self.clients}"

class ContactUs(TranslatableModel):
    translations = TranslatedFields(
        address = models.TextField()
    )
    phone = models.CharField(max_length=100)
    email = models.EmailField()
    istagram = models.URLField()
    telegram = models.URLField()
    facebook = models.URLField()
    youtube = models.URLField()

    
class Review(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='Review/')
    text = models.TextField()
    
    def __str__(self):
        return self.name
    
class DriverRequest(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    closed = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"