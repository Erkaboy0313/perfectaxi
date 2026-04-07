from category.models import CarService
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from utils.cordinates import FindRoute
from utils.cache_functions import setKey, getKey, removeKey
from .serializers import CostSerializer
from .views import (
    createOrder, lastOrderClient, lastOrderDriver,
    removeDriverLocation, setDriverLocation,
    setClientOnlineStatus, setDriverOnlineStatus,
    getOnlineDrivers, cancelTask, sendOrderToDriverView,
    get_order, start_drive, finish_drive, cancel_drive,
    arrive_address, check_balance, go_online, set_busy,
)
from users.models import Driver
from .ws_codes import (
    WS_SUCCESS,
    WS_INVALID_TOKEN,
    WS_INSUFFICIENT_FUND,
    WS_ORDER_NOT_FOUND,
    WS_ORDER_TAKEN,
    WS_CANCEL_FAILED,
)


class OrderConsumer(WebsocketConsumer):

    # ── Auth decorator ────────────────────────────────────────────────────────

    def isAuthenticatedC(func):
        def wrapper(self, *args, **kwargs):
            user = self.scope["user"]
            if user.is_authenticated:
                if user.role == "driver":
                    res = check_balance(user)
                    if res:
                        self.accept()
                        return self.send_error("Insufficient Fund", code=WS_INSUFFICIENT_FUND)
                return func(self, *args, **kwargs)
            else:
                self.accept()
                return self.send_error("Invalid Token", code=WS_INVALID_TOKEN)
        return wrapper

    # ── Connect / Disconnect ──────────────────────────────────────────────────

    @isAuthenticatedC
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name
        self.accept()
        user = self.scope['user']
        if user.role == 'driver':
            self.join_room(f'driver_{user.id}')
            driver = Driver.objects.get(user=user)
            self.order_status({"action": "profile", "message": driver.status})
            prev_not = getKey(f"new_order_driver_{user.id}")
            if prev_not:
                self.send_order_to_driver({"message": prev_not})
            res = lastOrderDriver(user)
            if res:
                return self.send_order(res)
        elif user.role == 'client':
            self.join_room(f'client_{user.id}')
            setClientOnlineStatus(user, True)
            res = lastOrderClient(user)
            if res:
                return self.send_order(res)

    def disconnect(self, close_code):
        user = self.scope['user']
        cancelTask(f'sendtaskclient_{user.id}')
        if user.role == 'driver':
            setDriverOnlineStatus(user, False)
        elif user.role == 'client':
            setClientOnlineStatus(user, False)
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    # ── Command handlers ──────────────────────────────────────────────────────

    def calculatePrice(self, data):
        """
        {
            "command": "calculate_price",
            "start_point": "41.311190,69.253287",
            "points": ["41.336120,69.284654","41.311296,69.253709"],
            "service": []
        }
        """
        start = data.get('start_point')
        points = data.get('points', [])
        service = data.get('service', [])
        d = FindRoute().find_drive(start, points)
        costs = CarService.filter.calculatePrice(d, service)
        serializer = CostSerializer(costs, many=True)
        return self.send_price(serializer.data)

    def newOrder(self, data):
        user = self.scope['user']
        cancelTask(f'sendtaskclient_{user.id}')
        order, service = createOrder(user, data)
        sendOrderToDriverView(f"order_{order['id']}", user.id, data['start_point'], service)
        return self.send_order(order)

    def findDrivers(self, data):
        location = data.get('location', '')
        user = self.scope['user']
        if location:
            getOnlineDrivers(f'client_{user.id}', location)

    def getOrder(self, data):
        user = self.scope['user']
        cancelTask(f"order_{data['order_id']}")
        res = get_order(user, data)
        if res:
            async_to_sync(self.channel_layer.group_send)(
                f"client_{res[2].client.user.id}",
                {'type': 'send_driver_user', 'driver': res[1]}
            )
            return self.send_order_driver(res[0])
        else:
            return self.send_error("Order already taken", code=WS_ORDER_TAKEN)

    def arriveDestination(self, data):
        res = arrive_address(data)
        if res:
            client_group = f'client_{res.client.user.id}'
            response_data = {
                "message": {"order_id": res.id, "message": "Driver arrived"},
                "action": "driver_arrived"
            }
            self.order_status(response_data)
            return self.send_message_to_group(client_group, response_data['message'], "arrived")
        else:
            return self.send_error("Order not found", code=WS_ORDER_NOT_FOUND)

    def startDrive(self, data):
        res = start_drive(data)
        if res:
            client_group = f'client_{res.client.user.id}'
            response_data = {
                "message": {"order_id": res.id, "message": "order started"},
                "action": "start_drive"
            }
            self.order_status(response_data)
            return self.send_message_to_group(client_group, response_data['message'], "start_drive")
        else:
            return self.send_error("Order not found", code=WS_ORDER_NOT_FOUND)

    def finishDrive(self, data):
        res = finish_drive(data)
        if res:
            client_group = f'client_{res.client.user.id}'
            response_data = {
                "message": {"order_id": res.id, "message": "order finished", "price": res.price},
                "action": "finish_drive"
            }
            self.order_status(response_data)
            return self.send_message_to_group(client_group, response_data['message'], "finish_drive")
        else:
            return self.send_error("Order not found", code=WS_ORDER_NOT_FOUND)

    def cancelDrive(self, data):
        status, res = cancel_drive(data)
        if status:
            driver_group = f'driver_{res.driver.user.id}'
            response_data = {
                "message": {"order_id": res.id, "message": "order canceled"},
                "action": "cancel_drive"
            }
            self.order_status(response_data)
            return self.send_message_to_group(driver_group, response_data['message'], "cancel_drive")
        else:
            return self.send_error("Cancel failed", code=WS_CANCEL_FAILED)

    def goOnline(self, data):
        user = self.scope['user']
        res = check_balance(user)
        if res:
            return self.send_error("Insufficient Fund", code=WS_INSUFFICIENT_FUND)
        go_online(user)
        return self.order_status({'action': "user_online", "message": "you are online"})

    def setBusy(self, data):
        user = self.scope['user']
        set_busy(user)
        removeDriverLocation(user)
        return self.order_status({'action': "user_busy", "message": "you are offline"})

    def seen_order(self, data):
        order_id = data['order_id']
        order = getKey(f"prew_driver_{order_id}")
        if order['driver_id'] == self.scope['user'].id:
            order['seen'] = True
            setKey(f"prew_driver_{order_id}", order)

    def miss_order(self, data):
        order_id = data['order_id']
        user_id = self.scope['user'].id
        removeKey(f"prew_driver_{order_id}")
        removeKey(f"new_order_driver_{user_id}")

    commands = {
        'find_drivers': findDrivers,
        'calculate_price': calculatePrice,
        'new_order': newOrder,
        'get_order': getOrder,
        'arrive_drive': arriveDestination,
        'start_drive': startDrive,
        'finish_drive': finishDrive,
        'cancel_drive': cancelDrive,
        'go_online': goOnline,
        'set_busy': setBusy,
        'seen_order': seen_order,
        'miss_order': miss_order,
    }

    def receive(self, text_data):
        data = json.loads(text_data)
        self.commands[data['command']](self, data)

    # ── Group helpers ─────────────────────────────────────────────────────────

    def send_message_to_group(self, group, data, action):
        async_to_sync(self.channel_layer.group_send)(
            group,
            {"type": "order_status", "message": data, "action": action}
        )

    def join_room(self, *args):
        for room_name in args:
            print(f'user joined -> {room_name}')
            async_to_sync(self.channel_layer.group_add)(room_name, self.channel_name)

    # ── Outgoing send methods ─────────────────────────────────────────────────
    # All success messages:  {"code": 1, "action": "<action>", "data": <payload>}
    # All error messages:    {"code": <negative int>, "error_message": "<text>"}

    def order_status(self, data):
        """Direct call and group_send handler (type: order_status)."""
        if isinstance(data, dict) and 'type' in data:
            action = data.get('action', '')
            message = data.get('message', None)
        else:
            action = data['action']
            message = data['message']
        self.send(text_data=json.dumps({
            "code": WS_SUCCESS,
            "action": action,
            "data": message,
        }))

    def send_order_to_driver(self, order):
        self.send(text_data=json.dumps({
            "code": WS_SUCCESS,
            "action": "new_order",
            "data": order['message'],
        }))

    def send_failur_message_to_client(self, event):
        self.send(text_data=json.dumps({
            "code": WS_SUCCESS,
            "action": "failed",
            "data": "couldn't find drivers",
        }))

    def send_error(self, event_or_message, code=None):
        """
        Dual-use:
          Direct call:   self.send_error("message", code=WS_ORDER_NOT_FOUND)
          Group send:    {'type': 'send_error', 'message': '...', 'code': -3}
        """
        if isinstance(event_or_message, dict) and 'type' in event_or_message:
            message = str(event_or_message.get('message', 'Unknown error'))
            error_code = event_or_message.get('code', WS_ORDER_NOT_FOUND)
        else:
            if isinstance(event_or_message, dict):
                message = event_or_message.get('error_text', str(event_or_message))
            else:
                message = str(event_or_message)
            error_code = code if code is not None else WS_ORDER_NOT_FOUND
        self.send(text_data=json.dumps({
            "code": error_code,
            "error_message": message,
        }))

    def notify_missed_order(self, event):
        """Group send handler: driver did not respond to an order in time."""
        message = event.get('message', '') if isinstance(event, dict) else event
        self.send(text_data=json.dumps({
            "code": WS_SUCCESS,
            "action": "miss_order",
            "data": message,
        }))

    def send_order(self, massage):
        self.send(text_data=json.dumps({
            "code": WS_SUCCESS,
            "action": "order",
            "data": massage,
        }))

    def send_order_driver(self, massage):
        self.send(text_data=json.dumps({
            "code": WS_SUCCESS,
            "action": "order",
            "data": massage,
        }))

    def send_driver_user(self, massage):
        self.send(text_data=json.dumps({
            "code": WS_SUCCESS,
            "action": "driver",
            "data": massage['driver'],
        }))

    def send_drivers(self, event):
        self.send(text_data=json.dumps({
            "code": WS_SUCCESS,
            "action": "drivers",
            "data": event['message'],
        }))

    def send_driver_location(self, event):
        self.send(text_data=json.dumps({
            "code": WS_SUCCESS,
            "action": "driver_location",
            "data": event['message'],
        }))

    def send_price(self, massage):
        self.send(text_data=json.dumps({
            "code": WS_SUCCESS,
            "action": "price",
            "data": massage,
        }))

    def chat_message(self, event):
        self.send(text_data=json.dumps({
            "code": WS_SUCCESS,
            "action": "chat_message",
            "data": event["message"],
        }))

    def send_to_group(self, orders, *args):
        for room_name in args:
            async_to_sync(self.channel_layer.group_send)(
                room_name,
                {'type': 'chat_message', 'message': orders}
            )


class LocationConsumer(WebsocketConsumer):

    def isAuthenticatedC(func):
        def wrapper(self, *args, **kwargs):
            user = self.scope["user"]
            if user.is_authenticated:
                return func(self, *args, **kwargs)
            else:
                self.accept()
                return self.send_error("Invalid Token", code=WS_INVALID_TOKEN)
        return wrapper

    @isAuthenticatedC
    def connect(self):
        self.room_name = "Locations"
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_name, self.channel_name
        )

    def setLocation(self, data):
        """
        {
            "command": "set_location",
            "location": "41.322548,69.210607"
        }
        """
        from .views import setDriverLocation
        user = self.scope['user']
        location = data.get('location', '')
        if location:
            setDriverLocation(user, location)

    commands = {
        'set_location': setLocation,
    }

    def receive(self, text_data):
        data = json.loads(text_data)
        self.commands[data['command']](self, data)

    def send_error(self, event_or_message, code=None):
        if isinstance(event_or_message, dict) and 'type' in event_or_message:
            message = str(event_or_message.get('message', 'Unknown error'))
            error_code = event_or_message.get('code', WS_ORDER_NOT_FOUND)
        else:
            message = str(event_or_message)
            error_code = code if code is not None else WS_ORDER_NOT_FOUND
        self.send(text_data=json.dumps({
            "code": error_code,
            "error_message": message,
        }))
