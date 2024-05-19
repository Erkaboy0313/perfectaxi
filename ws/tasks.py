# Create your tasks here
from celery import shared_task
from utils.findDrivers import findCloseDriver,findAvailableDrivers
from asgiref.sync import async_to_sync
from utils.cache_functions import sgetKey,ssetKey,sremoveKey
from channels.layers import get_channel_layer 
from django_celery_beat.models import PeriodicTask
from order.models import Order
from users.models import Driver
from pricing.models import PricingDriver
from payment.models import Balance,Charge
from utils.cordinates import remove_location
from .models import TaskCount,SearchRadius

@shared_task(name = 'sendDriverLocation')
def sendDriverLocation(user,location,service):
    channel_layer = get_channel_layer()
    drivers = findCloseDriver(location=location,service=service)
    return async_to_sync(channel_layer.group_send)(
        user,
        {
            'type':'send_drivers',
            'message': drivers
        }
    )

@shared_task(name = "sendActiveDriver")
def sendActiveDriverLocation(driver,user,location = None):
    if location:
        channel_layer = get_channel_layer()
        data = {
            "driver":Driver.objects.get(user__id = driver).id,

            "c_loc":{"latitude":float(location.split(",")[0]),
                     "longitude":float(location.split(",")[1])},

            "p_loc":{"latitude":float(sgetKey(f"prev_loc_{int(driver)}").split(",")[0]),
                     "longitude":float(sgetKey(f"prev_loc_{int(driver)}").split(",")[1])}
        }

        ssetKey(f"prev_loc_{int(driver)}",location)

        return async_to_sync(channel_layer.group_send)(
            user,
            {
                'type':"send_driver_location",
                'message':data
            }
        )

@shared_task(name = "set_redis_keys")
def setRedisKeys(order_data,driver_id):
    order_id = order_data['order']
    black_list = sgetKey(f"black_list_{order_id}")
    if black_list:
        black_list.append(driver_id)
    else:
        black_list = [driver_id]
        
    ssetKey(f"black_list_{order_id}",black_list)
    ssetKey(f'new_order_driver_{driver_id}',order_data)
    ssetKey(f"prew_driver_{order_id}",{"driver_id":driver_id,"seen":False})

@shared_task(name = 'notify_prev_driver')
def notify_prev_driver(order_id):
    prev_driver = sgetKey(f"prew_driver_{order_id}")
    if prev_driver:
        driver = Driver.objects.get(user_id=prev_driver['driver_id'])
        if prev_driver['seen']:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"driver_{prev_driver['driver_id']}",
                {
                    'type':'notify_missed_order',
                    'message':"you missed order"
                }
            )
        else:
            driver.status = Driver.DriverStatus.BUSY
            driver.save()
            remove_location(prev_driver['driver_id'])

        sremoveKey(f"prew_driver_{order_id}")
        sremoveKey(f'new_order_driver_{prev_driver["driver_id"]}')

@shared_task(name = 'find_drivers_to_order')
def find_drivers_to_order(order,location,service):
    
    order_id = order.split('_')[1]
    
    if Order.objects.filter(id = order_id,status = 'active').exists():
        drivers = sgetKey(order)
        radius = SearchRadius.objects.last()
        radiuses = [radius.radius1,radius.radius2,radius.radius3,radius.radius4]
        if not drivers:
            while not drivers and radiuses:
                print(radiuses[0])
                drivers = findAvailableDrivers(location=location,radius=radiuses.pop(0),order_id=order_id,service=service)
                print(f"-----------------------{drivers} -----------------------------")
            ssetKey(order,drivers)
            
    else:
        task = PeriodicTask.objects.get(name = f"find_{order}")
        task.enabled = False
        task.save()

@shared_task(name = 'sendOrderToDriver')
def sendOrderTodriverTask(order,client):
    
    order_id = order.split('_')[1]
    notify_prev_driver.delay(order_id)
    
    task = PeriodicTask.objects.get(name = order)

    if Order.objects.filter(id = order_id,status = 'active').exists():
        channel_layer = get_channel_layer()
        task_count,created = TaskCount.objects.get_or_create(name = order)
        task_count.inc

        drivers = sgetKey(order)
        if task_count.count <= 6 and drivers:
            driver = drivers.pop(0)
            ssetKey(order,drivers)
        
            order_data = {
                        "order":order_id,
                        "distance":driver['distance'],
                        "time":round(driver['time']/60)       
                        }
            setRedisKeys.delay(order_data,driver["id"])
            
            async_to_sync(channel_layer.group_send)(
                f"driver_{driver['id']}",
                {
                    # should send more details about order
                    'type':'send_order_to_driver',
                    'message':order_data
                }
            )

        elif task_count.count > 6:
            task.enabled = False
            task.save()

            sremoveKey(order)
            sremoveKey(f"black_list_{order_id}")

            active_order = Order.objects.get(id = order_id)
            active_order.status = 'inactive'
            active_order.save()

            async_to_sync(channel_layer.group_send)(
                f"client_{client}",
                {
                    'type':'send_failur_message_to_client'
                }
            )
    
    else:
        task.enabled = False
        task.save()        
        sremoveKey(order)
        sremoveKey(f"black_list_{order_id}")
    
    return True

@shared_task(name = 'Insufficientfund')
def insufficientfund(driver_id):
    channel_layer = get_channel_layer()
    remove_location(driver_id)
    driver = Driver.objects.get(user__id = driver_id)
    driver.status = Driver.DriverStatus.BUSY
    driver.save()
    return async_to_sync(channel_layer.group_send)(
        f"driver_{driver_id}",
        {
            'type':'send_error',
            'message': {"error_text":"Insufficient Fund"}
        }
    )

@shared_task(name = 'Charge Driver')
def charge_driver(order_id,driver_id):
    order = Order.objects.get(id = order_id)
    balance = Balance.objects.get(driver__id = driver_id)
    charge_price = round(order.price * (PricingDriver.objects.last().price / 100),0)
    balance.fund -= charge_price
    balance.save()
    Charge.objects.create(balance = balance,order=order,charged_fund = charge_price,status = Charge.ChargeStatus.SUCCESS)
    if balance.fund < 5000:
        insufficientfund.delay(balance.driver.user.id)
