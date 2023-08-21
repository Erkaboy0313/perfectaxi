from category.models import CarService
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from utils.calculateDistance import caculateDistance
from .serializers import CostSerializer
from .views import createOrder

class OrderConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )


    def calculatePrice(self,data):
        """
            {
                "command":"calculate_price",
                "start_point":"69.253287,41.311190",
                "points":["69.284654,41.336120","69.253709,41.311296"],
                "service":[]
            }
        """
        start = data.get('start_point')
        points = data.get('points',[])
        service = data.get('service',[])
        d = caculateDistance(start,points)
        costs = CarService.filter.calculatePrice(d,service)
        serializer = CostSerializer(costs,many=True)
        # Send message to room group
        return self.send_price(serializer.data)

    def newOrder(self,data):
        """
            {
                "command":"new_order",
                "start_point":"69.253287,41.311190",
                "points":["69.284654,41.336120","69.253709,41.311296"],
                "carservice":1,
                "price":11640.0,
                "services":[],
            }
        """
        order = createOrder(self.scope['user'],data)
        return self.send_order(order)

    commands = {
        'calculate_price':calculatePrice,
        'new_order':newOrder
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
    # send order to user
    def send_order(self , massage):
        self.send(text_data=json.dumps(
                {   
                    "action":"order",
                    'message':massage
                }
            )) 
           
    # send drivers location to user
    def send_drivers(self , massage):
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


class LocationConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "chat_message", "message": message}
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        self.send(text_data=json.dumps({"message": message}))