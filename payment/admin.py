from django.contrib import admin
from .models import Balance,Payment,Charge

admin.site.register(Payment)

@admin.register(Balance)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id_number','driver')

admin.site.register(Charge)
# Register your models here.
