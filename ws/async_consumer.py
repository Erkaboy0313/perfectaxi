from channels.generic.websocket import AsyncWebsocketConsumer
from category.models import CarService
from users.models import Driver
from order.models import DriverOrderHistory,Order

from utils.cordinates import FindRoute

from utils.cache_functions import setKey,getKey,removeKey

from .async_view import createOrder,lastOrderClient,lastOrderDriver,lastOrderDriver,\
    setDriverLocation,removeDriverLocation,setDriverOnlineStatus,setClientOnlineStatus,\
        getOnlineDrivers,cancelTask,get_order,arrive_address,\
            start_drive,finish_drive,cancel_drive,check_balance,go_online,set_busy

from .tasks import sendOrderTodriverTask

from .async_serializer import costSerializer
import json


class OrderConsumer(AsyncWebsocketConsumer):
    
    def isAuthenticatedC(func):
        async def wrapper(self,*args,**kwargs):
            user = self.scope["user"]
            if user.is_authenticated:
                if user.role == "driver":

                    if not user.is_verified:
                        await self.accept()
                        return await self.send_error({"error_text":"User is not verified"})
                    
                    res = await check_balance(user)
                    if res:
                        await self.accept()
                        return await self.send_error({"error_text":"Insufficient Fund"})
                    
                return await func(self,*args,**kwargs)
            else:
                await self.accept()
                await self.send_error({"error_text":"Invalid Token"})
                return self.close()
        return wrapper
    
    @isAuthenticatedC
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name

        # Accept the connection
        await self.accept()

        user = self.scope['user']
        
        if user.role == 'driver':
            await self.join_room(f'driver_{user.id}')
            driver = await Driver.objects.aget(user=user)
            await self.order_status({
                "action": "profile",
                "message": driver.status
            })
            
            prev_not = await getKey(f"new_order_driver_{user.id}")
            if prev_not:
                await self.send_order_to_driver({"message": prev_not})
            res = await lastOrderDriver(user)  # Assuming lastOrderDriver is async
            if res:
                return await self.send_order(res)

        elif user.role == 'client':
            await self.join_room(f'client_{user.id}')
            await setClientOnlineStatus(user, True)  # Assuming setClientOnlineStatus is async
            res = await lastOrderClient(user)  # Assuming lastOrderClient is async
            if res:
                return await self.send_order(res)

    async def disconnect(self, close_code):
        user = self.scope['user']
        await cancelTask(f'sendtaskclient_{user.id}')  
        if user.role == 'driver':
            print('driver removed')
            await removeDriverLocation(user)
            await setDriverOnlineStatus(user, False)  
        elif user.role == 'client':
            await setClientOnlineStatus(user, False)  

        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )
    
    # need to be fixed
    async def calculatePrice(self, data):
        lat = data.get('latitude')
        long = data.get('longitude')
        start = f"{lat},{long}"
        sorted_points = sorted(data.get('points', []),key=lambda x: x['point_number'])
        points = [f"{x['latitude']},{x['longitude']}" for x in sorted_points]
        service = data.get('service', [])
        distance,time = await FindRoute().find_drive(start, points)  # Assuming find_drive is async
        costs = await CarService.filter.calculatePrice(distance=distance,time=time,service_list=service)  # Assuming calculatePrice is async
        serialized_data = await costSerializer(costs)
        return await self.send_price(serialized_data)  # Assuming send_price is async

    async def newOrder(self, data):
        user = self.scope['user']
        await cancelTask(f'sendtaskclient_{user.id}')  # Assuming cancelTask is async

        strat_point = f"{data['latitude']},{data['longitude']}"
        order, order_obj = await createOrder(user, data)  # Assuming createOrder is async

        sendOrderTodriverTask.delay(f"order_{order_obj.id}", strat_point, order_obj.carservice.service)
        
        return await self.send_order(order)  # Assuming send_order is async

    # need to be fixed
    async def findDrivers(self, data):
        location = f"{data.get('latitude')},{data.get('longitude')}"
        user = self.scope['user']
        service = data.get('service',None)
        if location:
            await getOnlineDrivers(f'client_{user.id}', location, service) 

    async def getOrder(self, data):
        user = self.scope['user']

        res = await get_order(user, data)  # Assuming get_order is async
        if res:
            await self.channel_layer.group_send(  # Using await directly for async channel_layer
                f"client_{res[1].client.user.id}",
                {
                    'type': 'send_driver_user',
                    'driver': await lastOrderClient(res[1].client.user)
                }
            )
            return await self.send_order_driver(res[0])  # Assuming send_order_driver is async
        else:
            return await self.send_error('order olindi')  # Assuming send_error is async

    async def arriveDestination(self, data):
        
        res = await arrive_address(data)  # Assuming arrive_address is async
        if res:
            client_group = f'client_{res.client.user.id}'
            response_data = {
                "message": {
                    "order_id": res.id,
                    "message": "Driver arrived",
                },
                "action": "driver_arrived"
            }
            action = "arrived"
            await self.order_status(response_data)  # Assuming order_status is async
            return await self.send_message_to_group(client_group, response_data['message'], action)  # Assuming send_message_to_group is async
        else:
            return await self.send_error("order not found")  # Assuming send_error is async
        
    async def startDrive(self, data):

        res = await start_drive(data)  # Assuming start_drive is async
        if res:
            client_group = f'client_{res.client.user.id}'
            response_data = {
                "message": {
                    "order_id": res.id,
                    "message": "order started",
                },
                "action": "start_drive"
            }
            action = "start_drive"
            await self.order_status(response_data)  # Assuming order_status is async
            return await self.send_message_to_group(client_group, response_data['message'], action)  # Assuming send_message_to_group is async
        else:
            return await self.send_error("order not found")  # Assuming send_error is async

    async def finishDrive(self, data):
        res = await finish_drive(data)  # Assuming finish_drive is async
        if res:
            client_group = f'client_{res.client.user.id}'
            response_data = {
                "message": {
                    "order_id": res.id,
                    "message": "order finished",
                    "price": res.price
                },
                "action": "finish_drive"
            }
            action = "finish_drive"
            await self.order_status(response_data)  # Assuming order_status is async
            return await self.send_message_to_group(client_group, response_data['message'], action)  # Assuming send_message_to_group is async
        else:
            return await self.send_error("order not found")

    async def cancelDrive(self, data):
        status, res = await cancel_drive(data)  # Assuming cancel_drive is async
        if status:
            
            extra_data = await getKey(f'order_extra_info_{res.id}')
            extra_data['status'] = 'canceled'
            await setKey(f'order_extra_info_{res.id}',extra_data)
            
            response_data = {
                "message": {
                    "order_id": res.id,
                    "message": "order canceled",
                },
                "action": "cancel_drive"
            }
            action = "cancel_drive"
            
            if res.driver:
                driver_group = f'driver_{res.driver.user.id}'
                await self.send_message_to_group(driver_group, response_data['message'], action)  # Assuming send_message_to_group is async
            
            user = self.scope['user']
            res = await lastOrderClient(user)  # Assuming lastOrderClient is async
            await self.order_status(response_data)  # Assuming order_status is async
            return await self.send_order(res)
        else:
            return await self.send_error(res)
    
    async def goOnline(self, data):
        user = self.scope['user']
        res = await check_balance(user)  # Assuming check_balance is async
        if res:
            return self.send_error({"error_text": "Insufficient Fund"})
        await go_online(user)  # Assuming go_online is async
        data = {
            'action': "user_online",
            "message": "you are online"
        }
        return await self.order_status(data)  # Assuming order_status is async

    async def setBusy(self, data):
        user = self.scope['user']
        await set_busy(user)  # Assuming set_busy is async
        await removeDriverLocation(user)  # Assuming removeDriverLocation is async
        data = {
            'action': "user_busy",
            "message": "you are offline"
        }
        return await self.order_status(data)  # Assuming order_status is async

    async def seen_order(self, data):
        order_id = data['order_id']
        data = await getKey(f'active_order_{order_id}')
        if data:  
            if data['driver'] == self.scope['user'].id:
                data['status'] = 'seen'
                await setKey(f'active_order_{order_id}',data)

    async def miss_order(self, data):
        try:
            order_id = data['order_id']
            user_id = self.scope['user'].id
            order = await Order.objects.aget(id = order_id)
            driver = await Driver.objects.aget(user__id = user_id)
            await removeKey(f"prew_driver_{order_id}")  # Assuming removeKey is async
            await removeKey(f"new_order_driver_{user_id}")  # Assuming removeKey is async
            await DriverOrderHistory.objects.acreate(driver=driver, order = order, status = order.OrderStatus.REJECTED)
            
            data = await getKey(f'active_order_{order.id}')
            if data:  
                if data['driver'] == self.scope['user'].id:
                    data['status'] = 'rejected'
                    await setKey(f'active_order_{order.id}',data)
            
            sendOrderTodriverTask.delay(f"order_{order['id']}", order.start_point, order.carservice.service)
            
            # Other logic here
        except:
            return await self.send_error('order not found')

    async def setLocation(self, data):
        """
            {
                "command":"set_location",
                "location":"41.322548, 69.210607"                   
            }
        """
        user = self.scope['user']
        location = f"{data.get('latitude')},{data.get('longitude')}"
        if location:
            await setDriverLocation(user, location)  # Assuming setDriverLocation is async

    async def set_payment(self, data):
        """
        {
            "command":"set_payment",
            "payment_type":cash or card
            "order_id":id
        }
        """
        order = await Order.objects.aget(id = data.get('order_id'))
        order.payment_type = data.get("payment_type")
        await order.save()
        return self.send(json.dumps({"action":"set_payment",
                                     "payment_type":data['payment_type'],
                                     'order_id':data['order_id']}))

    commands = {
        'find_drivers':findDrivers,
        'calculate_price':calculatePrice,
        'new_order':newOrder,
        'get_order':getOrder,
        'arrive_drive':arriveDestination,
        'start_drive':startDrive,
        'finish_drive':finishDrive,
        'cancel_drive':cancelDrive,
        'go_online':goOnline,
        'set_busy':setBusy,
        'seen_order':seen_order,
        'miss_order':miss_order,
        'set_location':setLocation,
        'set_payment':set_payment,
    }

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.commands[data['command']](self, data)  # Call async commands directly

    async def send_message_to_group(self, group, data, action):
        await self.channel_layer.group_send(  # Direct async call
            group,
            {
                "type": "order_status",
                "message": data,
                "action": action
            }
        )

    async def order_status(self, data):
        await self.send(  # Assuming self.send is async
            text_data=json.dumps(
                {
                    "action": data['action'],
                    "message": data['message']
                }
            )
        )

    async def send_to_group(self, orders, *args):
        for room_name in args:
            await self.channel_layer.group_send(  # Direct async call
                room_name,
                {
                    'type': 'chat_message',
                    'order': orders
                }
            )
            
    # send new order to driver
    async def send_order_to_driver(self, order):
        await self.send(  # Assuming self.send is async
            text_data=json.dumps(
                {
                    "action": "new_order",
                    "message": order["message"]
                }
            )
        )
        
    # send info about search is failed to user  
    async def send_failur_message_to_client(self, event):
        await self.send(  # Assuming self.send is async
            text_data=json.dumps(
                {
                    "action": "failed",
                    "message": await lastOrderClient(event['user'])
                }
            )
        )
        
    # send error to user
    async def send_error(self, massage):
        await self.send(  # Assuming self.send is async
            text_data=json.dumps(
                {
                    "action": "error",
                    "message": massage
                }
            )
        )

    async def notify_missed_order(self, massage):
        await self.send(  # Assuming self.send is async
            text_data=json.dumps(
                {
                    "action": "miss_order",
                    "message": massage
                }
            )
        )
        
    # send order to user
    async def send_order(self, massage):
        await self.send(  # Assuming self.send is async
            text_data=json.dumps(
                {
                    "action": "order",
                    "message": massage
                }
            )
        )
        
    # send order to driver
    async def send_order_driver(self, massage):
        await self.send(  # Assuming self.send is async
            text_data=json.dumps(
                {
                    "action": "order",
                    "message": massage
                }
            )
        )
        
    # send driver info to user
    async def send_driver_user(self, massage):
        await self.send(  # Assuming self.send is async
            text_data=json.dumps(
                {
                    "action": "driver",
                    "message": massage["driver"]
                }
            )
        )
        
    # send drivers location to user
    async def send_drivers(self, event):
        massage = event["message"]
        await self.send(  # Assuming self.send is async
            text_data=json.dumps(
                {
                    "action": "drivers",
                    "message": massage
                }
            )
        )
        
    # send the location of the driver who received the order to user
    async def send_driver_location(self, event):
        data = event["message"]
        await self.send(  # Assuming self.send is async
            text_data=json.dumps(
                {
                    "action": "driver_location",
                    "message": data
                }
            )
        )
        
    # send price to user
    async def send_price(self, massage):
        await self.send(  # Assuming self.send is async
            text_data=json.dumps(
                {
                    "action": "price",
                    "message": massage
                }
            )
        )
        
    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        await self.send(  # Assuming self.send is async
            text_data=json.dumps({"message": message})
        )
        
    # join room
    async def join_room(self, *args):
        for room_name in args:
            print(f"user joined -> {room_name}")
            await self.channel_layer.group_add(  # Direct async call
                room_name,
                self.channel_name
            )
