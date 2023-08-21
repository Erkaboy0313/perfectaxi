from django.db.models import Manager
from django.db.models import F
from order.models import Services


class CategoryManager(Manager):

    def calculatePrice(self,d,serivice_list):
        def multipy(a,b,d,service_list):
            service_cost = Services.filter.sumSerivies(serivice_list)
            return a+(b*d)+service_cost
        return self.get_queryset().annotate(cost=multipy(F('start_price'),d,F('price_per_km'),serivice_list))

