from django.contrib import admin
from .models import User,Driver,Client,Admin,DocumentImages,DriverAvailableService
# Register your models here.    

admin.site.register(User)
admin.site.register(Driver)
admin.site.register(Admin)
admin.site.register(Client)
admin.site.register(DocumentImages)
admin.site.register(DriverAvailableService)