from order.serializers import OrderSeriazer,Order
from users.models import Client
from utils.cache_functions import setKey,getKey,getKeys
from django.db.models import Q
from django_celery_beat.models import PeriodicTask,IntervalSchedule
from .tasks import sendDriverLocation,sendOrderTodriverTask
import json
from datetime import datetime
from .serializers import OrderToDriverSerializer,DriverInfoSerializer
from users.serializers import Driver

def createOrder(user,data):
    client = Client.objects.get(user=user)
    serializer = OrderSeriazer(data=data)
    serializer.is_valid(raise_exception=True)
    data = serializer.save(client = client)
    serializer = OrderSeriazer(data)
    return serializer.data

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
        return (order.data,driver.data,_order)
    return False

def lastOrderClient(user):
    lastOrder = Order.objects.filter(client__user = user).exclude(Q(status = "delivered") | Q(status = "rejected")).last()
    if lastOrder:
        serializer = OrderSeriazer(lastOrder)
        return serializer.data
    else:
        return False

def lastOrderDriver(user):
    lastOrder = Order.objects.filter(driver__user = user).exclude(Q(status = "delivered") | Q(status = "rejected")).last()
    if lastOrder:
        serializer = OrderSeriazer(lastOrder)
        return serializer.data
    else:
        return False

def setDriverLocation(user,location):
    location = {
        "user":f"driver_{user.id}",
        "location":location
    }
    setKey(f'DL_{user.id}',location)

def setDriverOnlineStatus(user,is_online):
    data = {
        "is_online":is_online,
    }
    setKey(f'US_{user.id}',data)

def setClientOnlineStatus(user,is_online):
    data = {
        "is_online":is_online,
    }
    setKey(f'CS_{user.id}',data)

def getOnlineDrivers(user):
    sendDriverLocation.delay(user)
    interval,created = IntervalSchedule.objects.get_or_create(every=10, period=IntervalSchedule.SECONDS)
    task,created = PeriodicTask.objects.get_or_create(name = f"sendtask{user}", interval = interval)
    task.task = 'sendDriverLocation'
    task.args = json.dumps([user])
    task.enabled = True
    task.save()

def sendOrderToDriverView(order,user):
    interval,created = IntervalSchedule.objects.get_or_create(every=10, period=IntervalSchedule.SECONDS)
    task = PeriodicTask.objects.create(name = order, interval = interval)
    
    sendOrderTodriverTask.delay(order,user)
    
    task.task = 'sendOrderToDriver'
    task.args = json.dumps([order,user])
    task.save()

def cancelTask(user):
    task,created = PeriodicTask.objects.get_or_create(name = f'sendtask{user}')
    task.enabled = False
    task.save()

