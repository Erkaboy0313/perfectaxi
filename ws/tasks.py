# Create your tasks here
from celery import shared_task
from utils.findDrivers import findCloseDriver,OrderDriversByRoute
from asgiref.sync import async_to_sync
from utils.cache_functions import getKey,setKey
from channels.layers import get_channel_layer 
from django_celery_beat.models import PeriodicTask
from order.models import Order
from users.models import Driver
from utils.cordinates import retrieve_location

@shared_task(name = 'sendDriverLocation')
def sendDriverLocation(user,location):
    channel_layer = get_channel_layer()
    drivers = findCloseDriver(location=location)
    return async_to_sync(channel_layer.group_send)(
        user,
        {
            'type':'send_drivers',
            'message': drivers
        }
    )

@shared_task(name = "sendActiveDriver")
def sendActiveDriverLocation(driver,user,location = None):
    channel_layer = get_channel_layer()
    data = {
        "driver":Driver.objects.get(user__id = driver).id, #id
        "location":retrieve_location(driver) if not location else location
    }
    print(data)
    return async_to_sync(channel_layer.group_send)(
        user,
        {
            'type':"send_driver_location",
            'message':data
        }
    )

@shared_task(name = 'sendOrderToDriver')
def sendOrderTodriverTask(order,client,location):
    order_id = order.split('_')[1]
    channel_layer = get_channel_layer()
    task = PeriodicTask.objects.get(name = order)
    
    drivers = getKey(order)
    driver = None

    if type(drivers) == list and drivers:
        driver = drivers.pop(0)
        setKey(order,drivers)
    elif drivers == None :
        # should sort drivers according to rout
        drivers = findCloseDriver(location=location)
        ordered_drivers = OrderDriversByRoute(drivers,location)
        if ordered_drivers:
            driver = ordered_drivers.pop(0)
            setKey(order,ordered_drivers)
    else:
        task.enabled = False
        task.save()
        if Order.objects.filter(id = order_id,status = 'active').exists():
            async_to_sync(channel_layer.group_send)(
                f"client_{client}",
                {
                    'type':'send_failur_message_to_client'
                }
            )
    
    if driver:
        if Order.objects.filter(id = order_id,status = 'active').exists():
            print('sending message to driver')
            async_to_sync(channel_layer.group_send)(
                f"driver_{int(driver[0])}",
                {
                    #should send more details about order
                    'type':'send_order_to_driver',
                    'message':{"order":order_id}
                }
            )
        else:
            task.enabled = False
            task.save()        

    return True
    