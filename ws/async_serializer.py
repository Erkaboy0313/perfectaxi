from order.models import Point

async def costSerializer(data):
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
    for cost in data:
        obj = {
            'id':cost['id'],
            'service':cost['service'],
            'cost':await roundPrice(cost['cost']),
            'travel_time':cost['travel_time'],
            'distance':cost['distance'],
        }
        cost_list.append(obj)

    return cost_list

async def point(x):
    return {
        "point_number":x.point_number,
        "address":x.point_address,
        "latitude":float(x.point.split(',')[0]),
        "longitude":float(x.point.split(',')[1])
    }

async def orderSeriazer(data):
    obj = {
        "id":data.id,
        "client":data.client.id,
        "driver":None,
        "carservice":data.carservice.service,
        "contact_number":data.contact_number,
        "start_adress":data.start_adress,
        "latitude":float(data.start_point.split(',')[0]),
        "longitude":float(data.start_point.split(',')[1]),
        "points":[await point(x) async for x in Point.objects.filter(order = data)],
        "distance":data.distance,
        "price":data.price,
        "payment_type":data.payment_type,
        "services":[x.name for x in data.services.all()]
    }
    return obj

async def driverInfoSerializer(data):
    obj = {
        "id" : data.id,
        "name" : await data.aname,
        "profile_image" : await data.aprofile_image,
        "car_model" : data.car_model,
        "car_name" : data.car_name,
        "car_number" : data.car_number,
        "car_color" : data.car_color
    }
    return obj

async def lastOrderserializer(data):
    orders = []
    async for order in data:
        obj = {
            "id":order.id,
            "client":order.client.id,
            "status":order.status,
            "driver":await driverInfoSerializer(order.driver) if order.driver else None,
            "carservice":order.carservice.service,
            "contact_number":order.contact_number,
            "start_adress":order.start_adress,
            "latitude":float(order.start_point.split(',')[0]),
            "longitude":float(order.start_point.split(',')[1]),
            "points":[await point(x) async for x in Point.objects.filter(order = order)],
            "distance":order.distance,
            "price":order.price,
            "payment_type":order.payment_type,
            "services":[x.name for x in order.services.all()]
        }
        orders.append(obj)
    return orders

async def orderToDriverSerializer(data):
    obj = {
        "id":data.id,
        "contact_number":data.contact_number,
        "start_adress":data.start_adress,
        "latitude":float(data.start_point.split(',')[0]),
        "longitude":float(data.start_point.split(',')[1]),
        "price":data.price,
        "payment_type":data.payment_type,
        "status":data.status,
        "services":[x.name for x in data.services.all()],
        "points":[await point(x) async for x in Point.objects.filter(order = data)]
    }
    return obj
