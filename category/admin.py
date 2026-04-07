from django.contrib import admin
from parler.admin import TranslatableAdmin
from .models import CarService, SavedLocation, CarBrend, Color, CarModel, Log


admin.site.register(Log)
admin.site.register(SavedLocation)
admin.site.register(CarService, TranslatableAdmin)
admin.site.register(CarBrend, TranslatableAdmin)
admin.site.register(Color, TranslatableAdmin)
admin.site.register(CarModel, TranslatableAdmin)
