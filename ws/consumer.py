from category.models import CarService
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from utils.calculateDistance import caculateDistance
from utils.findDrivers import findCloseDriver
from utils.cache_functions import getKey,setKey
from .serializers import CostSerializer
from .views import createOrder,lastOrderClient,lastOrderDriver
from .views import setDriverLocation,setClientOnlineStatus,\
        setDriverOnlineStatus,getOnlineDrivers,cancelTask,\
        sendOrderToDriverView,get_order


class OrderConsumer(WebsocketConsumer):

    def isAuthenticatedC(func):
        def wrapper(self,*args,**kwargs):
            user = self.scope["user"]
            if user.is_authenticated:
                return func(self,*args,**kwargs)
            else:
                self.accept()
                self.send_error({"error_text":"Invalid Token"})
        return wrapper
    
    def isAuthenticated(func):
        def wrapper(self,*args,**kwargs):
            user = self.scope["user"]
            if user.is_authenticated:
                return func(self,*args,**kwargs)
            else:
                self.send_error({"error_text":"Invalid Token"})
        return wrapper

    @isAuthenticatedC
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name   

        self.accept()
        user = self.scope['user']
        print(user.role)
        if user.role == 'driver':
            setDriverOnlineStatus(user,True)
            self.join_room(f'driver_{user.id}')
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
        cancelTask(f'client_{user.id}')
        if user.role == 'driver':
            setDriverOnlineStatus(user,False)
        elif user.role == 'client':
            setClientOnlineStatus(user,False)

        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    @isAuthenticated
    def calculatePrice(self,data):
        """
            {
                "command":"calculate_price",
                "start_point":"69.253287,41.311190",
                "points":["69.284654,41.336120","69.253709,41.311296"],
                "service":[]
            }
        """
        user = self.scope['user']
        start = data.get('start_point')
        points = data.get('points',[])
        service = data.get('service',[])

        d = caculateDistance(start,points)
        costs = CarService.filter.calculatePrice(d,service)
        serializer = CostSerializer(costs,many=True)
        getOnlineDrivers(f'client_{user.id}')
        return self.send_price(serializer.data)
    
    @isAuthenticated
    def newOrder(self,data):
        """
            {
                "command":"new_order",
                "start_point":"69.253287,41.311190",
                "points":["69.284654,41.336120","69.253709,41.311296"],
                "carservice":1,
                "price":11640.0,
                "services":[]
            }
        """
        user = self.scope['user']
        cancelTask(f'client_{user.id}')

        # should send a location and function will find closest and available drivers.
        drivers = findCloseDriver(location="location")
        order = createOrder(user,data)
        setKey(f"order_{order['id']}",drivers)

        # should provide with more info about order
        sendOrderToDriverView(f"order_{order['id']}",user.id)

        return self.send_order(order)


    @isAuthenticated
    def getOrder(self,data):
        # Driver accepts order
        user = self.scope['user']
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

    commands = {
        'calculate_price':calculatePrice,
        'new_order':newOrder,
        'get_order':getOrder
    }

    # Receive message from WebSocket
    def receive(self, text_data):
        data = json.loads(text_data)
        self.commands[data['command']](self , data)

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

    @OrderConsumer.isAuthenticatedC
    def connect(self):
        self.room_name = "Locations"
        # Join room group

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    @OrderConsumer.isAuthenticated
    def setLocation(self,data):
        """
            {
                "command":"set_location",
                "location":"69.253287,41.311190"
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

