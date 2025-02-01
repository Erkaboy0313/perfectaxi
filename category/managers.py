from django.db.models import Manager
from order.models import Services


class CategoryManager(Manager):

    async def calculatePrice(self,distance,time,service_list):
        async def roundPrice(price):
            rounded_hundreds = int(price / 100) % 10  # Extract the hundreds part and round it
            if rounded_hundreds >= 7:
                rounded_price = int(price / 1000) * 1000 + 1000
            elif rounded_hundreds >= 3:
                rounded_price = int(price / 1000) * 1000 + 500
            else:
                rounded_price = int(price / 1000) * 1000
            return rounded_price

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
                'cost':await roundPrice(cost),
                'travel_time':time,
                'distance':distance,
            }
            cost_list.append(obj)
            
        return cost_list
            
