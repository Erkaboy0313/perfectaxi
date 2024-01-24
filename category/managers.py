from django.db.models import Manager
from django.db.models import F
from order.models import Services
import asyncio


class CategoryManager(Manager):

    async def calculatePrice(self,distance,time,service_list):
        
        # async def multipy(a,b,d,service_list):
        #     service_cost = await Services.filter.sumSerivies(service_list)
        #     return a+(b*d)+service_cost
        
        # return self.annotate(cost=await multipy(F('start_price'),d,F('price_per_km'),service_list))

        cost_list = []
        service_cost = await Services.filter.sumSerivies(service_list)
        async for category in self.all():
            
            cost = category.start_price + service_cost
            if distance > 1:
                cost += (distance - 1) * category.price_per_km
            if time > 3:        
                cost += (time - 3) * category.price_per_min 
                
            #price multiplier should be added here
            
            obj = {
                'id':category.id,
                'service':category.service,
                'cost':cost,
                'travel_time':time,
                'distance':distance,
            }
            cost_list.append(obj)
            
        return cost_list
            
