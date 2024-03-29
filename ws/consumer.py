from category.models import CarService
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer,AsyncWebsocketConsumer
from utils.cordinates import FindRoute
from utils.cache_functions import setKey
from .serializers import CostSerializer
from .views import createOrder,lastOrderClient,lastOrderDriver,removeDriverLocation
from .views import setDriverLocation,setClientOnlineStatus,\
        setDriverOnlineStatus,getOnlineDrivers,cancelTask,\
        sendOrderToDriverView,get_order,start_drive,finish_drive,cancel_drive,\
        arrive_address,check_balance,go_online,set_busy
from utils.cache_functions import getKey,setKey,removeKey
from users.models import Driver

class OrderConsumer(WebsocketConsumer):

    def isAuthenticatedC(func):
        def wrapper(self,*args,**kwargs):
            user = self.scope["user"]
            if user.is_authenticated:
                if user.role == "driver":
                    res = check_balance(user)
                    if res:
                        self.accept()
                        return self.send_error({"error_text":"Insufficient Fund"})
                return func(self,*args,**kwargs)
            else:
                self.accept()
                return self.send_error({"error_text":"Invalid Token"})
        return wrapper

    @isAuthenticatedC
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name   
        self.accept()
        user = self.scope['user']
        if user.role == 'driver':
            self.join_room(f'driver_{user.id}')
            driver = Driver.objects.get(user = user)
            self.order_status({
                "action":"profile",
                "message":driver.status
            })
            prev_not = getKey(f"new_order_driver_{user.id}")
            if prev_not:
                self.send_order_to_driver({"message":prev_not})
            res = lastOrderDriver(user)
            if res:
                return self.send_order(res)
            
        elif user.role == 'client':
            self.join_room(f'client_{user.id}')
            setClientOnlineStatus(user,True)
            res = lastOrderClient(user)
            if res:
                return self.send_order(res)

    def disconnect(self, close_code):
        # Leave room group
        user = self.scope['user']
        cancelTask(f'sendtaskclient_{user.id}')
        if user.role == 'driver':
            setDriverOnlineStatus(user,False)
        elif user.role == 'client':
            setClientOnlineStatus(user,False)

        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def calculatePrice(self,data):
        """
            {
                "command":"calculate_price",
                "start_point":"41.311190,69.253287",
                "points":["41.336120,69.284654","41.311296,69.253709"],
                "service":[]
            }
        """
        start = data.get('start_point')
        points = data.get('points',[])
        service = data.get('service',[])
        d = FindRoute().find_drive(start,points)
        costs = CarService.filter.calculatePrice(d,service)
        serializer = CostSerializer(costs,many=True)
        
        return self.send_price(serializer.data)
    
    def newOrder(self,data):
        """
            {
                "command":"new_order",
                "start_point":"41.285409, 69.226037",
                "points":["41.336120,69.284654","41.311296,69.253709"],
                "carservice":1,
                "price":11640.0,
                "services":[]
            }
        """
        user = self.scope['user']
        cancelTask(f'sendtaskclient_{user.id}')

        # should send a location and function will find closest and available drivers.
        order,service = createOrder(user,data)

        # should provide with more info about order
        sendOrderToDriverView(f"order_{order['id']}",user.id,data['start_point'],service)

        return self.send_order(order)

    def findDrivers(self,data):
        """
            {
                "command":"find_drivers",
                "location":"41.322548, 69.210607"
            }
        """
        location = data.get('location','')
        user = self.scope['user']
        if location:
            getOnlineDrivers(f'client_{user.id}',location)

    def getOrder(self,data):
        # Driver accepts order
        """
            {
                "command":"get_order",
                "order_id":3
            }
        """

        user = self.scope['user']
        cancelTask(f"order_{data['order_id']}")
        res = get_order(user,data)
        if res:
            async_to_sync(self.channel_layer.group_send)(
                f"client_{res[2].client.user.id}",
                {
                    'type': 'send_driver_user',
                    'driver': res[1]
                }
            )
            return self.send_order_driver(res[0])
        else:
            return self.send_error('order olindi')

    def arriveDestination(self,data):
        """
            {
                "command":"arrive_drive",
                "order_id":id
            }
        """
        res = arrive_address(data)
        if res:
            client_group = f'client_{res.client.user.id}'
            response_data = {
                "message":{
                    "order_id":res.id,
                    "message":"Driver arrived",
                },
                "action":"driver_arrived"
                }
            action = "start_drive"
            self.order_status(response_data)
            return self.send_message_to_group(client_group,response_data['message'],action)
        else:
            return self.send_error("order not found")

    def startDrive(self,data):
        """
            {
                "command":"start_drive",
                "order_id":id
            }
        """
        res = start_drive(data)
        if res:
            client_group = f'client_{res.client.user.id}'
            response_data = {
                "message":{
                    "order_id":res.id,
                    "message":"order started",
                },
                "action":"start_drive"
                }
            action = "start_drive"
            self.order_status(response_data)
            return self.send_message_to_group(client_group,response_data['message'],action)
        else:
            return self.send_error("order not found")

    def finishDrive(self,data):
        """
            {
                "command":"finish_drive",
                "order_id":id,
                "tottal_distance": 12.5 #Optinal. in km
            }
        """
        res = finish_drive(data)
        if res:
            client_group = f'client_{res.client.user.id}'
            response_data = {
                "message":{
                    "order_id":res.id,
                    "message":"order finished",
                    "price":res.price
                },
                "action":"finish_drive"
                }
            action = "finish_drive"
            self.order_status(response_data)
            return self.send_message_to_group(client_group,response_data['message'],action)
        else:
            return self.send_error("order not found")
        
    # should Be updated. Remove Active driver key from redis if driver exists    
    def cancelDrive(self,data):
        """
            {
                "command":"cancel_drive",
                "order_id":id,
                "reason":id,
                "comment":str,optional
            }
        """
        status,res = cancel_drive(data)
        if status:
            driver_group = f'driver_{res.driver.user.id}'
            response_data = {
                "message":{
                    "order_id":res.id,
                    "message":"order canceled",
                },
                "action":"cancel_drive"
                }
            action = "cancel_drive"
            self.order_status(response_data)
            return self.send_message_to_group(driver_group,response_data['message'],action)
        else:
            return self.send_error(res)

    def goOnline(self,data):
        user = self.scope['user']
        res = check_balance(user)
        if res:
            return self.send_error({"error_text":"Insufficient Fund"})
        go_online(user)
        data = {
            'action':"user_online",
            "message":"you are online"
        }
        return self.order_status(data)

    def setBusy(self,data):
        user = self.scope['user']
        set_busy(user)
        removeDriverLocation(user)
        data = {
            'action':"user_busy",
            "message":"you are offline"
        }
        return self.order_status(data)

    def seen_order(self,data):
        order_id = data['order_id']
        order = getKey(f"prew_driver_{order_id}")
        if order['driver_id'] == self.scope['user'].id:
            order['seen'] = True
            setKey(f"prew_driver_{order_id}",order)

    def miss_order(self,data):
        order_id = data['order_id']
        user_id = self.scope['user'].id
        removeKey(f"prew_driver_{order_id}")
        removeKey(f"new_order_driver_{user_id}")
        # Other logic here

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
    }

    # Receive message from WebSocket
    def receive(self, text_data):
        data = json.loads(text_data)
        self.commands[data['command']](self , data)

    def send_message_to_group(self,group,data,action):
        async_to_sync(self.channel_layer.group_send)(
            group,{
                "type":'order_status',
                "message":data,
                "action":action
            }
        )
    
    def order_status(self,data):
        self.send(
            text_data=json.dumps(
                {
                    "action":data['action'],
                    "message":data['message']
                }
            )
        )

    def send_to_group(self,orders,*args):
        for room_name in args:
            async_to_sync(self.channel_layer.group_send)(
                room_name,
                {
                    'type': 'chat_message',
                    'order': orders
                }
            )

    # send new order to driver
    def send_order_to_driver(self,order):
        
        self.send(text_data=json.dumps(
            {   
                "action":"new_order",
                'message': order['message']
            }
        ))

    # send info about search is failed to user  
    def send_failur_message_to_client(self,event):

        self.send(text_data=json.dumps(
            {
                "action":"failed",
                'message': "couldn't find drivers"
            }
        ))

    # send error to user
    def send_error(self , massage):
        self.send(text_data=json.dumps(
            {   
                "action":"error",
                'message':massage
            }
        )) 

    def notify_missed_order(self, massage):
        self.send(text_data=json.dumps(
            {   
                "action":"miss_order",
                'message': massage
            }
        ))

    # send order to user
    def send_order(self , massage):
        self.send(text_data=json.dumps(
            {   
                "action":"order",
                'message':massage
            }
        ))

    # send order to driver
    def send_order_driver(self , massage):
        self.send(text_data=json.dumps(
            {   
                "action":"order",
                'message':massage
            }
        )) 

    # send driver info to user
    def send_driver_user(self , massage):
        self.send(text_data=json.dumps(
            {   
                "action":"driver",
                'message':massage['driver']
            }
        )) 
           
    # send drivers location to user
    def send_drivers(self , event):
        massage = event['message']
        self.send(text_data=json.dumps(
            {   
                "action":"drivers",
                'message':massage
            }
        ))

    # send the location of the driver who received the order to user
    def send_driver_location(self,event):
        data = event['message']
        self.send(text_data=json.dumps(
            {
                "action":"driver_location",
                "message":data
            }
        ))
           
    # send price to user
    def send_price(self , massage):
        self.send(text_data=json.dumps(
                {   
                    "action":"price",
                    'message':massage
                }
            ))    

    # Receive message from room group
    def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        self.send(text_data=json.dumps({"message": message}))

    # join room
    def join_room(self,*args):
        for room_name in args:
            print(f'user joined -> {room_name}')
            async_to_sync(self.channel_layer.group_add)(
                room_name,
                self.channel_name
            )

class LocationConsumer(WebsocketConsumer):

    def isAuthenticatedC(func):
        def wrapper(self,*args,**kwargs):
            user = self.scope["user"]
            if user.is_authenticated:
                return func(self,*args,**kwargs)
            else:
                self.accept()
                return self.send_error({"error_text":"Invalid Token"})
        return wrapper

    @isAuthenticatedC
    def connect(self):
        self.room_name = "Locations"
        # Join room group

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_name, self.channel_name
        )

    def setLocation(self,data):
        """
            {
                "command":"set_location",
                "location":"41.322548, 69.210607"                   
            }
        """
        user = self.scope['user']
        location = data.get('location','')
        if location:
            setDriverLocation(user,location)
        
    commands = {
        'set_location':setLocation,
    }

    # Receive message from WebSocket
    def receive(self, text_data):
        data = json.loads(text_data)
        self.commands[data['command']](self , data)

    # send error to user
    def send_error(self , massage):
        self.send(text_data=json.dumps(
                {   
                    "action":"error",
                    'message':massage
                }
            )) 
