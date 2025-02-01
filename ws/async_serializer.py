from order.models import Point

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
        "status":data.status,
        "driver":None,
        "carservice":await carServiceSerialzier(data.carservice),
        "contact_number":data.contact_number,
        "start_adress":data.start_adress,
        "latitude":float(data.start_point.split(',')[0]),
        "longitude":float(data.start_point.split(',')[1]),
        "points":[await point(x) async for x in Point.objects.filter(order = data)],
        "distance":data.distance,
        "price":data.price,
        "payment_type":data.payment_type,
        "services":await ServiceSerializer(data.services.all())
    }
    return obj

async def driverInfoSerializer(data):
    obj = {
        "id" : data.id,
        "first_name" : data.user.first_name,
        "last_name" : data.user.last_name,
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
            "carservice":await carServiceSerialzier(order.carservice),
            "contact_number":order.contact_number,
            "start_adress":order.start_adress,
            "latitude":float(order.start_point.split(',')[0]),
            "longitude":float(order.start_point.split(',')[1]),
            "points":[await point(x) async for x in Point.objects.filter(order = order)],
            "distance":order.distance,
            "price":order.price,
            "payment_type":order.payment_type,
            "services":await ServiceSerializer(order.services.all())
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
        "services":await ServiceSerializer(data.services.all()),
        "points":[await point(x) async for x in Point.objects.filter(order = data)]
    }
    return obj

async def ServiceSerializer(services):
    return [{"id":x.id,"name":x.name,'cost':x.cost} async for x in services]

async def carServiceSerialzier(car_service):
    return {
        'id':car_service.id,
        'service':car_service.service,
        'includedCars':car_service.includedCars,
        'start_price':car_service.start_price,
    }
