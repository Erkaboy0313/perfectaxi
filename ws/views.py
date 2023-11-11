from order.serializers import OrderSeriazer,Order
from users.models import Client
from utils.cache_functions import setKey,getKey,removeKey
from utils.cordinates import update_driver_location,remove_location
from django.db.models import Q
from django_celery_beat.models import PeriodicTask,IntervalSchedule
from .tasks import sendDriverLocation,sendOrderTodriverTask,sendActiveDriverLocation
import json
from datetime import datetime
from .serializers import OrderToDriverSerializer,DriverInfoSerializer,LastOrderSerializer
from users.serializers import Driver

# create new order(Client)
def createOrder(user,data):
    client = Client.objects.get(user=user)
    serializer = OrderSeriazer(data=data)
    serializer.is_valid(raise_exception=True)
    data = serializer.save(client = client)
    serializer = OrderSeriazer(data)
    return serializer.data

# client's last orders
def lastOrderClient(user):
    last_orders = Order.objects.filter(client__user = user).exclude(Q(status = "delivered") | Q(status = "rejected"))
    if last_orders:
        serializer = LastOrderSerializer(last_orders,many=True)
        return serializer.data
    else:
        return False

# Drivers last orders
def lastOrderDriver(user):
    lastOrder = Order.objects.filter(driver__user = user).exclude(Q(status = "delivered") | Q(status = "rejected")).last()
    if lastOrder:
        serializer = OrderSeriazer(lastOrder)
        return serializer.data
    else:
        return False

def setDriverLocation(user,location):
    long,lat = list(map(float,location.split(',')))
    data = getKey(f"active_driver_{user.id}")
    if data:
        sendActiveDriverLocation.delay(user.id,data,(lat,long))
    update_driver_location(user.id,lat,long)

def removeDriverLocation(user):
    remove_location(user.id)

def setDriverOnlineStatus(user,is_online):
    pass

def setClientOnlineStatus(user,is_online):
    data = {
        "is_online":is_online,
    }
    setKey(f'CS_{user.id}',data)

def getOnlineDrivers(user,location):
    sendDriverLocation.delay(user,location)
    interval,created = IntervalSchedule.objects.get_or_create(every=10, period=IntervalSchedule.SECONDS)
    task,created = PeriodicTask.objects.get_or_create(name = f"sendtask{user}", interval = interval)
    task.task = 'sendDriverLocation'
    task.args = json.dumps([user,location])
    task.enabled = True
    task.save() 

def sendOrderToDriverView(order,user,location):
    interval,created = IntervalSchedule.objects.get_or_create(every=10, period=IntervalSchedule.SECONDS)
    task = PeriodicTask.objects.create(name = order, interval = interval)
    sendOrderTodriverTask.delay(order,user,location)    
    task.task = 'sendOrderToDriver'
    task.args = json.dumps([order,user,location])
    task.save()

def cancelTask(name):
    task,created = PeriodicTask.objects.get_or_create(name = name)
    task.enabled = False
    task.save()

# take order (Driver)
def get_order(user,data):
    driver = Driver.objects.get(user=user)
    _order = Order.objects.filter(id = data['order_id'],status = Order.OrderStatus.ACTIVE).first()
    if _order:
        _order.driver = driver
        _order.taken_time = datetime.now()
        _order.status = Order.OrderStatus.DELIVERING
        _order.save()
        order = OrderToDriverSerializer(_order)
        driver = DriverInfoSerializer(driver)
        setKey(f"active_driver_{user.id}",f"client_{_order.client.user.id}")
        sendActiveDriverLocation.delay(user.id,f"client_{_order.client.user.id}")
        return (order.data,driver.data,_order)
    return False

def arrive_address(data):
    order = data.get('order_id',None)
    if order:
        order = Order.objects.get(id = int(order))
        order.save(arrive = True)
        return order
    else:
        return False

def start_drive(data):
    order = data.get('order_id',None)
    if order:
        order = Order.objects.get(id = int(order))
        order.status = 'delivering'
        order.save(start = True)
        return order
    else:
        return False

def finish_drive(data):
    order = data.get('order_id',None)
    if order:
        order = Order.objects.get(id = int(order))
        order.status = 'delivered'
        order.save(finish=True)
        removeKey(f"active_driver_{order.driver.user.id}")
        return order
    else:
        return False

def cancel_drive(data):
    order = data.get('order_id',None)
    if order:
        order = Order.objects.get(id = int(order))
        order.status = 'rejected'
        order.save(reject = True)
        return order
    else:
        return False
    