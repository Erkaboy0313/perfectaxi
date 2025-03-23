from django.contrib import admin
from .models import AppLinks,Service,Pricing,Statistic,Review,DriverRequest,ContactUs
from parler.admin import TranslatableAdmin


@admin.register(Service)
class ServiceAdmin(TranslatableAdmin):
    list_display = ("name","title")

@admin.register(ContactUs)
class ContactUsAdmin(TranslatableAdmin):
    list_display = ("phone","email")

@admin.register(Pricing)
class PricingAdmin(TranslatableAdmin):
    list_display = ("name",)

@admin.register(Statistic)
class StatisticAdmin(TranslatableAdmin):
    list_display = ("avilable_drivers","clients","drivers","rides")

admin.site.register(AppLinks)
admin.site.register(Review)
admin.site.register(DriverRequest)