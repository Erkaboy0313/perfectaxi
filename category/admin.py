from django.contrib import admin
from .models import CarService,SavedLocation,CarBrend,Color,CarModel,Log


# Register your models here.

admin.site.register(Log)
admin.site.register(CarService)
admin.site.register(SavedLocation)
admin.site.register(CarBrend)
admin.site.register(Color)
admin.site.register(CarModel)