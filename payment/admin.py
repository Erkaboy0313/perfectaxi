from django.contrib import admin
from .models import Balance,Payment,Charge

admin.site.register(Balance)
admin.site.register(Payment)
admin.site.register(Charge)
# Register your models here.
