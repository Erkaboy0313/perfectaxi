from users.models import Client,Driver
from order.models import Order,RejectReason,DriverOrderHistory
from order.serializers import OrderCreateSeriazer
from django.db.models import Q
from payment.models import Balance
from django_celery_beat.models import PeriodicTask,IntervalSchedule
from utils.cache_functions import setKey,getKey,removeKey
from utils.cordinates import update_driver_location,remove_location,aremove_location
from datetime import datetime
from .tasks import sendDriverLocation,sendActiveDriverLocation,charge_driver
from .async_serializer import lastOrderserializer,orderToDriverSerializer
import asyncio,functools
import json

# Create new order (Client)
async def createOrder(user, data, extra_data):
    # Get the client object associated with the user
    client = await Client.objects.aget(user=user)  # Assuming Client.objects.get is async

    # Validate and serialize the order data
    serializer = OrderCreateSeriazer(data=data)
    await asyncio.to_thread(functools.partial(serializer.is_valid,raise_exception=True))
    data = await asyncio.to_thread(functools.partial(serializer.save,client=client,price = extra_data['cost'],distance = extra_data['distance']))
    
    order = await Order.objects.select_related('carservice').aget(id = data.id)
    
    await setKey(f"order_extra_info_{order.id}",{"price":order.price,"start_adress":order.start_adress,'status':order.status},timeout=600)

    serialized_data = await lastOrderClient(user)

    # Return both the serialized order data and the service associated with the order
    return (serialized_data, order)

# Client's last orders
async def lastOrderClient(user):
    # Retrieve orders for the client, excluding specific statuses
    last_orders = Order.objects.select_related('client','driver','driver__user','carservice').prefetch_related("services").filter( 
        client__user=user
    ).exclude(
        Q(status="delivered") | Q(status="rejected") | Q(status="inactive")
    )

    # If orders exist, serialize them
    if await last_orders.aexists():
        serialized_data = await lastOrderserializer(last_orders)
        return serialized_data
    else:
        return []  # Indicate no orders found
    
# Driver's last orders
async def lastOrderDriver(user):
    # Retrieve the last order for the driver, excluding specific statuses
    lastOrder = await Order.objects.select_related('client','driver','carservice').prefetch_related('services').filter(  # Assuming filter is async
        driver__user=user
    ).exclude(
        Q(status="delivered") | Q(status="rejected")
    ).alast()

    # If an order exists, serialize it
    if lastOrder:
        serialized_data = await orderToDriverSerializer(lastOrder)
        return serialized_data
    else:
        return False  # Indicate no orders found

async def setDriverLocation(user, location):
    long, lat = list(map(float, location.split(',')))
    
    data = await getKey(f"active_driver_{user.id}")
    if data:
        sendActiveDriverLocation.delay(user.id, data, location)
    else:
        driver = await Driver.objects.aget(user=user)
        if driver.status == Driver.DriverStatus.ACTIVE:
            await update_driver_location(user.id, lat, long)

async def removeDriverLocation(user):
    remove_location(user.id)  

async def setDriverOnlineStatus(user, is_online):
    pass  # Assuming already async or doesn't involve async operations

async def setClientOnlineStatus(user, is_online):
    data = {
        "is_online": is_online,
    }
    await setKey(f'CS_{user.id}', data)  # Assuming setKey is async

async def getOnlineDrivers(user, location, service):
    sendDriverLocation.delay(user, location, service)

    interval, created = await IntervalSchedule.objects.aget_or_create(  
        every=10, period=IntervalSchedule.SECONDS
    )
    task, created = await PeriodicTask.objects.aget_or_create(  
        name=f"sendtask{user}", interval=interval
    )
    task.task = 'sendDriverLocation'
    task.args = json.dumps([user, location, service])
    task.enabled = True
    await task.asave()  # Assuming save is async

async def cancelTask(name):
    try:
        task = await PeriodicTask.objects.aget(name=name)  
        task.enabled = False
        await task.asave()  # Assuming save is async
    except PeriodicTask.DoesNotExist:
        pass

async def get_order(user, data):
    driver = await Driver.objects.select_related('user').aget(user=user)  
    _order = await Order.objects.select_related('client','driver','driver__user','client__user').prefetch_related("services").filter(  # Assuming filter is async
        id=data['order_id'], status=Order.OrderStatus.ACTIVE
    ).afirst()
    await DriverOrderHistory.objects.acreate(driver=driver, order = _order, status = _order.OrderStatus.DELIVERING)

    if _order:
        _order.driver = driver
        _order.taken_time = datetime.now()
        _order.status = Order.OrderStatus.ASSIGNED
        await _order.asave()  # Assuming save is async

        order = await orderToDriverSerializer(_order)

        await setKey(  # Assuming setKey is async
            f"active_driver_{user.id}", f"client_{_order.client.user.id}"
        )
        sendActiveDriverLocation.delay(user.id, f"client_{_order.client.user.id}")
        
        # modify this later
        data = await getKey(f'active_order_{_order.id}')
        data['status'] = 'assigned'
        await setKey(f'active_order_{_order.id}',data)
        
        await removeKey(f"prew_driver_{_order.id}")  # Assuming removeKey is async
        await removeKey(f'new_order_driver_{user.id}')  # Assuming removeKey is async
        await aremove_location(user.id)
        return (order, _order)
    return False

async def arrive_address(data):
    try:
        order_id = data.get('order_id', None)
        order = await Order.objects.select_related('client','client__user').aget(id=int(order_id),status = Order.OrderStatus.ASSIGNED) 
        order.status = Order.OrderStatus.ARRIVED
        await order.asave(arrive=True)  # Assuming save is async
        return order
    except Exception as e:
        print(e)
        return False

async def start_drive(data):
    try:
        order_id = data.get('order_id', None)
        order = await Order.objects.select_related('client','client__user').aget(id=int(order_id),status = Order.OrderStatus.ARRIVED)  
        order.status = Order.OrderStatus.DELIVERING
        await order.asave(start=True)  # Assuming save is async        
        return order
    except Exception as e:
        print(e)
        return False

async def finish_drive(data):
    order_id = data.get('order_id', None)
    try:
        order = await Order.objects.select_related('client','client__user','driver','driver__user','carservice').aget(id=int(order_id),status = Order.OrderStatus.DELIVERING)  
        order.status = 'delivered'
        if not order.points.all().aexists():
            total_distance = data.get('total_distance', None)
            total_time = datetime.now() - order.started_time
            if total_distance:
                order.price += ((total_distance - 1) * order.carservice.price_per_km) + ((round(total_time.total_seconds()/60)-3) * order.carservice.price_per_min)

        await order.asave(finish=True)  # Assuming save is async
        charge_driver.delay(order.id, order.driver.id)
        await removeKey(f"active_driver_{order.driver.user.id}")  # Assuming removeKey is async
                
        driver_history = await DriverOrderHistory.objects.aget(order = order, driver= order.driver)
        driver_history.status = order.OrderStatus.DELIVERED
        await driver_history.asave()
        
        return order
    except Exception as e:
        print(e)
        return False

async def cancel_drive(data):
    order_id = data.get('order_id', None)
    reason = data.get('reason', None)
    comment = data.get('comment', None)
    if order_id and reason:
        try:
            order = await Order.objects.select_related('client','client__user','driver','driver__user').aget(id=int(order_id))  
            reject_reason = await RejectReason.objects.aget(id=int(reason))  
            order.status = 'rejected'
            order.reject_reason = reject_reason
            order.reject_comment = comment
            await order.asave(reject=True) # Assuming save is async
            if order.driver:
                
                driver_history = await DriverOrderHistory.objects.aget(order = order, driver= order.driver)
                driver_history.status = order.OrderStatus.REJECTED
                await driver_history.asave()
                    
                await removeKey(f'active_driver_{order.driver.user.id}') # Assuming removeKey is async
            return (True, order)
        except Order.DoesNotExist:
            return (False, "order not found")
        except Exception as e:
            return (False, f"{e}")
    else:
        return (False, "data incomplete")

async def check_balance(user):
    driver = await Driver.objects.aget(user=user)  
    balance = await Balance.objects.aget(driver=driver)  
    if balance.fund < 5000:
        driver.status = Driver.DriverStatus.BUSY
        await driver.asave()  # Assuming save is async
        return True
    return False

async def go_online(user):
    if user.role == 'driver':
        driver = await Driver.objects.aget(user=user)  
        driver.status = Driver.DriverStatus.ACTIVE
        await driver.asave()  # Assuming save is async
    return True

async def set_busy(user):
    if user.role == 'driver':
        driver = await Driver.objects.aget(user=user)  
        driver.status = Driver.DriverStatus.BUSY
        await driver.asave()  # Assuming save is async
        await aremove_location(user.id)
    return True

