from order.serializers import OrderSeriazer,Order,RejectReason
from users.models import Client
from utils.cache_functions import setKey,getKey,removeKey
from utils.cordinates import update_driver_location,remove_location
from django.db.models import Q
from django_celery_beat.models import PeriodicTask,IntervalSchedule
from .tasks import sendDriverLocation,sendActiveDriverLocation,charge_driver,find_drivers_to_order
import json
from datetime import datetime
from .serializers import OrderToDriverSerializer,DriverInfoSerializer,LastOrderSerializer
from users.serializers import Driver
from payment.models import Balance

# create new order(Client)
def createOrder(user,data):
    client = Client.objects.get(user=user)
    serializer = OrderSeriazer(data=data)
    serializer.is_valid(raise_exception=True)
    data = serializer.save(client = client)
    serializer = OrderSeriazer(data)
    return (serializer.data,data.carservice.service)

# client's last orders
def lastOrderClient(user):
    last_orders = Order.objects.filter(client__user = user).exclude(Q(status = "delivered") | Q(status = "rejected") | Q(status = "inactive"))
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
        sendActiveDriverLocation.delay(user.id,data,location)
    driver = Driver.objects.get(user = user)
    if driver.status == Driver.DriverStatus.ACTIVE:
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

def sendOrderToDriverView(order,user,location,service):
    interval,created = IntervalSchedule.objects.get_or_create(every=10, period=IntervalSchedule.SECONDS)
    interval2,created = IntervalSchedule.objects.get_or_create(every=5, period=IntervalSchedule.SECONDS)
    
    task = PeriodicTask.objects.create(name = order, interval = interval)
    task2 = PeriodicTask.objects.create(name = f"find_{order}",interval = interval2)

    find_drivers_to_order.delay(order,location,service)   

    task.task = 'sendOrderToDriver'
    task.args = json.dumps([order,user])
    task.save()

    task2.task = 'find_drivers_to_order'
    task2.args = json.dumps([order,location,service])
    task2.save()


def cancelTask(name):
    try:
        task = PeriodicTask.objects.get(name = name)
        task.enabled = False
        task.save()
    except:
        pass
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
        removeKey(f"prew_driver_{data['order_id']}")
        removeKey(f'new_order_driver_{user.id}')
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
    tottal_distance = data.get('tottal_distance',None)
    if order:
        order = Order.objects.get(id = int(order))
        order.status = 'delivered'
        if tottal_distance:
            order.price += tottal_distance * order.carservice.price_per_km
        order.save(finish=True)
        charge_driver.delay(order.id,order.driver.id)
        removeKey(f"active_driver_{order.driver.user.id}")        
        return order
    else:
        return False

def cancel_drive(data):
    order = data.get('order_id',None)
    reason = data.get('reason',None)
    comment = data.get('comment',None)
    if order and reason:
        try:
            order = Order.objects.get(id = int(order))
            reject_reason = RejectReason.objects.get(id = int(reason))
            order.status = 'rejected'
            order.reject_reason = reject_reason
            order.reject_comment = comment
            order.save(reject = True)
            if order.driver:
                removeKey(f'active_driver_{order.driver.user.id}')
            return (True,order)
        except:
            return (False,"order not found")
    else:
        return (False,"data incomplete")
    
def check_balance(user):
    driver = Driver.objects.get(user = user)
    balance = Balance.objects.get(driver = driver)
    if balance.fund < 5000:
        driver.status = Driver.DriverStatus.BUSY
        driver.save()
        return True
    return False

def go_online(user):
    if user.role == 'driver':
        driver = Driver.objects.get(user=user)
        driver.status = Driver.DriverStatus.ACTIVE
        driver.save()   
    return True

def set_busy(user):
    if user.role == 'driver':
        driver = Driver.objects.get(user=user)
        driver.status = Driver.DriverStatus.BUSY
        driver.save()
    return True

