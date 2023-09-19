# Create your tasks here
from celery import shared_task
from utils.findDrivers import findCloseDriver
from asgiref.sync import async_to_sync
from utils.cache_functions import getKey,setKey
from utils.findDrivers import findCloseDriver
from channels.layers import get_channel_layer 
from django_celery_beat.models import PeriodicTask
from order.models import Order
from .models import TaskCount

@shared_task(name = 'sendDriverLocation')
def sendDriverLocation(user):
    channel_layer = get_channel_layer()
    drivers = findCloseDriver()
    return async_to_sync(channel_layer.group_send)(
        user,
        {
            'type':'send_drivers',
            'message': drivers
        }
    )

@shared_task(name = 'sendOrderToDriver')
def sendOrderTodriverTask(order,client):
    order_id = order.split('_')[1]
    channel_layer = get_channel_layer()
    drivers = getKey(order)
    driver = None

    if drivers:
        
        driver = drivers.pop()
        setKey(order,drivers)

    else:
        # should give a location to find closest drivers for this location
        drivers = findCloseDriver(location='location',order=order)
        if drivers:
        
            driver = drivers.pop()
            setKey(order,drivers)

    taskcount , created = TaskCount.objects.get_or_create(name = order)
    task = PeriodicTask.objects.get(name = order)
    taskcount.count += 1
    taskcount.save()
    
    
    if driver:

        blacklist = getKey(f'b{order}')
        if blacklist:
            blacklist.append(driver)
            setKey(f"b{order}",blacklist)
        
        else:
            setKey(f'b{order}',[driver])

        if Order.objects.filter(id = order_id,status = 'active').exists():
            print('sending message to driver')
            async_to_sync(channel_layer.group_send)(
                driver['user'],
                {
                    #should send more details about order
                    'type':'send_order_to_driver',
                    'message':{"order":order_id}
                }
            )
        else:
            task.enabled = False
            task.save()        

    # Cancel Task after 6 times.
    if taskcount.count >= 6:
        task.enabled = False
        task.save()
        async_to_sync(channel_layer.group_send)(
            f"client_{client}",
            {
                'type':'send_failur_message_to_client'
            }
        )
    return True
    