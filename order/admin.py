from django.contrib import admin
from .models import Order,Point,Services,RejectReason,DriverOrderHistory

admin.site.register(Order)
admin.site.register(Point)
admin.site.register(Services)
admin.site.register(RejectReason)
admin.site.register(DriverOrderHistory)
# Register your models here.
