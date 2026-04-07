from channels.generic.websocket import AsyncWebsocketConsumer
from category.models import CarService
from users.models import Driver
from order.models import DriverOrderHistory, Order
from category.models import Log
from utils.cordinates import FindRoute
from utils.cache_functions import setKey, getKey, removeKey

from .async_view import (
    createOrder, lastOrderClient, lastOrderDriver,
    setDriverLocation, removeDriverLocation,
    setDriverOnlineStatus, setClientOnlineStatus,
    getOnlineDrivers, cancelTask, get_order, arrive_address,
    start_drive, finish_drive, cancel_drive,
    check_balance, go_online, set_busy,
)
from .tasks import sendOrderTodriverTask
from .async_serializer import orderToDriverSerializer
from .ws_codes import (
    WS_SUCCESS,
    WS_INVALID_TOKEN,
    WS_USER_NOT_VERIFIED,
    WS_INSUFFICIENT_FUND,
    WS_ORDER_NOT_FOUND,
    WS_ORDER_TAKEN,
    WS_PRICE_CALC_FAILED,
    WS_CANCEL_FAILED,
)
import json


class OrderConsumer(AsyncWebsocketConsumer):

    # ── Auth decorator ────────────────────────────────────────────────────────

    def isAuthenticatedC(func):
        async def wrapper(self, *args, **kwargs):
            user = self.scope["user"]
            if user.is_authenticated:
                if user.role == "driver":
                    if not user.is_verified:
                        await self.accept()
                        return await self.send_error("User is not verified", code=WS_USER_NOT_VERIFIED)

                    res = await check_balance(user)
                    if res:
                        await self.accept()
                        return await self.send_error("Insufficient Fund", code=WS_INSUFFICIENT_FUND)

                return await func(self, *args, **kwargs)
            else:
                await self.accept()
                await self.send_error("Invalid Token", code=WS_INVALID_TOKEN)
                return await self.close()
        return wrapper

    # ── Connect / Disconnect ──────────────────────────────────────────────────

    @isAuthenticatedC
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name

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
            res = await lastOrderDriver(user)
            if res:
                return await self.send_order(res)

        elif user.role == 'client':
            await self.join_room(f'client_{user.id}')
            await setClientOnlineStatus(user, True)
            res = await lastOrderClient(user)
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

        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        else:
            await self.channel_layer.group_discard("default", self.channel_name)

    # ── Command handlers ──────────────────────────────────────────────────────

    async def calculatePrice(self, data):
        lat = data.get('latitude')
        long = data.get('longitude')
        start = f"{lat},{long}"
        sorted_points = sorted(data.get('points', []), key=lambda x: x['point_number'])
        points = [f"{x['latitude']},{x['longitude']}" for x in sorted_points]
        service = data.get('service', [])
        distance, time = await FindRoute().find_drive(start, points)
        costs = await CarService.filter.calculatePrice(distance=distance, time=time, service_list=service)
        extra_data = [cost for cost in costs if cost['id'] == data['carservice']]
        print(extra_data)
        return extra_data[0] if extra_data else 0

    async def newOrder(self, data):
        user = self.scope['user']
        await cancelTask(f'sendtaskclient_{user.id}')
        strat_point = f"{data['latitude']},{data['longitude']}"

        extra_data = await self.calculatePrice(data)

        if not extra_data:
            return await self.send_error("Price calculation failed, please try again", code=WS_PRICE_CALC_FAILED)

        order, order_obj = await createOrder(user, data, extra_data)

        await Log.objects.acreate(text=f'{order_obj.id} uchun driver qidira boshlandi')
        sendOrderTodriverTask.delay(f"order_{order_obj.id}", strat_point, order_obj.carservice.service)

        return await self.send_order(order)

    async def findDrivers(self, data):
        location = f"{data.get('latitude')},{data.get('longitude')}"
        user = self.scope['user']
        service = data.get('service', None)
        if location:
            await getOnlineDrivers(f'client_{user.id}', location, service)

    async def getOrder(self, data):
        user = self.scope['user']
        res = await get_order(user, data)
        if res:
            await self.channel_layer.group_send(
                f"client_{res[1].client.user.id}",
                {'type': 'send_driver_user', 'driver': {"order_id": res[1].id}}
            )
            await self.channel_layer.group_send(
                f"client_{res[1].client.user.id}",
                {'type': 'send_order', 'orders': await lastOrderClient(res[1].client.user)}
            )
            return await self.send_order_driver(res[0])
        else:
            return await self.send_error("Order already taken", code=WS_ORDER_TAKEN)

    async def arriveDestination(self, data):
        res = await arrive_address(data)
        if res:
            client_group = f'client_{res.client.user.id}'
            response_data = {
                "message": {"order_id": res.id, "message": "Driver arrived"},
                "action": "driver_arrived"
            }
            await self.order_status(response_data)
            await self.send_order_driver(await orderToDriverSerializer(res))
            await self.send_message_to_group(client_group, response_data['message'], "arrived")
            await self.channel_layer.group_send(
                client_group,
                {'type': 'send_order', 'orders': await lastOrderClient(res.client.user)}
            )
        else:
            return await self.send_error("Order not found", code=WS_ORDER_NOT_FOUND)

    async def startDrive(self, data):
        res = await start_drive(data)
        if res:
            client_group = f'client_{res.client.user.id}'
            response_data = {
                "message": {"order_id": res.id, "message": "order started"},
                "action": "start_drive"
            }
            await self.order_status(response_data)
            await self.send_order_driver(await orderToDriverSerializer(res))
            await self.send_message_to_group(client_group, response_data['message'], "start_drive")
            await self.channel_layer.group_send(
                client_group,
                {'type': 'send_order', 'orders': await lastOrderClient(res.client.user)}
            )
        else:
            return await self.send_error("Order not found", code=WS_ORDER_NOT_FOUND)

    async def finishDrive(self, data):
        res = await finish_drive(data)
        if res:
            client_group = f'client_{res.client.user.id}'
            response_data = {
                "message": {"order_id": res.id, "message": "order finished", "price": res.price},
                "action": "finish_drive"
            }
            await self.order_status(response_data)
            await self.send_order_driver(await orderToDriverSerializer(res))
            await self.send_message_to_group(client_group, response_data['message'], "finish_drive")
            await self.channel_layer.group_send(
                client_group,
                {'type': 'send_order', 'orders': await lastOrderClient(res.client.user)}
            )
        else:
            return await self.send_error("Order not found", code=WS_ORDER_NOT_FOUND)

    async def cancelDrive(self, data):
        status, res = await cancel_drive(data)
        if status:
            extra_data = await getKey(f'order_extra_info_{res.id}')
            if extra_data:
                extra_data['status'] = 'canceled'
                await setKey(f'order_extra_info_{res.id}', extra_data)

            response_data = {
                "message": {"order_id": res.id, "message": "order canceled"},
                "action": "cancel_drive"
            }

            if res.driver:
                driver_group = f'driver_{res.driver.user.id}'
                await self.send_message_to_group(driver_group, response_data['message'], "cancel_drive")

            user = self.scope['user']
            res = await lastOrderClient(user)
            await self.order_status(response_data)
            return await self.send_order(res)
        else:
            return await self.send_error("Cancel failed", code=WS_CANCEL_FAILED)

    async def goOnline(self, data):
        user = self.scope['user']
        res = await check_balance(user)
        if res:
            return await self.send_error("Insufficient Fund", code=WS_INSUFFICIENT_FUND)
        await go_online(user)
        return await self.order_status({'action': "user_online", "message": "you are online"})

    async def setBusy(self, data):
        user = self.scope['user']
        await set_busy(user)
        await removeDriverLocation(user)
        return await self.order_status({'action': "user_busy", "message": "you are offline"})

    async def seen_order(self, data):
        order_id = data['order_id']
        cached = await getKey(f'active_order_{order_id}')
        if cached:
            if cached['driver'] == self.scope['user'].id:
                cached['status'] = 'seen'
                await setKey(f'active_order_{order_id}', cached)

    async def miss_order(self, data):
        try:
            order_id = data['order_id']
            user_id = self.scope['user'].id
            order = await Order.objects.aget(id=order_id)
            driver = await Driver.objects.aget(user__id=user_id)
            await removeKey(f"prew_driver_{order_id}")
            await removeKey(f"new_order_driver_{user_id}")
            await DriverOrderHistory.objects.acreate(
                driver=driver, order=order, status=order.OrderStatus.REJECTED
            )
            cached = await getKey(f'active_order_{order.id}')
            if cached:
                if cached['driver'] == self.scope['user'].id:
                    cached['status'] = 'rejected'
                    await setKey(f'active_order_{order.id}', cached)

            sendOrderTodriverTask.delay(f"order_{order['id']}", order.start_point, order.carservice.service)
        except Exception:
            return await self.send_error("Order not found", code=WS_ORDER_NOT_FOUND)

    async def setLocation(self, data):
        """
        {
            "command": "set_location",
            "latitude": 41.322548,
            "longitude": 69.210607
        }
        """
        user = self.scope['user']
        location = f"{data.get('latitude')},{data.get('longitude')}"
        if location:
            await setDriverLocation(user, location)

    async def set_payment(self, data):
        """
        {
            "command": "set_payment",
            "payment_type": "cash" | "card",
            "order_id": <id>
        }
        """
        order = await Order.objects.aget(id=data.get('order_id'))
        order.payment_type = data.get("payment_type")
        await order.asave()
        await self.send(text_data=json.dumps({
            "code": WS_SUCCESS,
            "action": "set_payment",
            "data": {
                "payment_type": data['payment_type'],
                "order_id": data['order_id'],
            }
        }))

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
        'set_location': setLocation,
        'set_payment': set_payment,
    }

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.commands[data['command']](self, data)

    # ── Group helpers ─────────────────────────────────────────────────────────

    async def send_message_to_group(self, group, data, action):
        await self.channel_layer.group_send(
            group,
            {"type": "order_status", "message": data, "action": action}
        )

    async def join_room(self, *args):
        for room_name in args:
            print(f"user joined -> {room_name}")
            await self.channel_layer.group_add(room_name, self.channel_name)

    # ── Outgoing send methods ─────────────────────────────────────────────────
    # All success messages:  {"code": 1, "action": "<action>", "data": <payload>}
    # All error messages:    {"code": <negative int>, "error_message": "<text>"}

    async def order_status(self, data):
        """Direct call and group_send handler (type: order_status)."""
        if isinstance(data, dict) and 'type' in data:
            # Dispatched by channel_layer.group_send
            action = data.get('action', '')
            message = data.get('message', None)
        else:
            action = data['action']
            message = data['message']
        await self.send(text_data=json.dumps({
            "code": WS_SUCCESS,
            "action": action,
            "data": message,
        }))

    async def send_order_to_driver(self, order):
        """Send a new incoming order to a driver."""
        await self.send(text_data=json.dumps({
            "code": WS_SUCCESS,
            "action": "new_order",
            "data": order["message"],
        }))

    async def send_failur_message_to_client(self, event):
        """Group send handler: no drivers found within timeout."""
        await self.send(text_data=json.dumps({
            "code": WS_SUCCESS,
            "action": "failed",
            "data": await lastOrderClient(event['user']),
        }))

    async def send_error(self, event_or_message, code=None):
        """
        Dual-use:
          Direct call:      await self.send_error("message", code=WS_ORDER_NOT_FOUND)
          Group send:       {'type': 'send_error', 'message': '...', 'code': -3}
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
        await self.send(text_data=json.dumps({
            "code": error_code,
            "error_message": message,
        }))

    async def notify_missed_order(self, event):
        """Group send handler: driver did not respond to an order in time."""
        message = event.get('message', '') if isinstance(event, dict) else event
        await self.send(text_data=json.dumps({
            "code": WS_SUCCESS,
            "action": "miss_order",
            "data": message,
        }))

    async def send_order(self, massage):
        """Send current order state to client or driver."""
        data = massage if "orders" not in massage else massage['orders']
        await self.send(text_data=json.dumps({
            "code": WS_SUCCESS,
            "action": "order",
            "data": data,
        }))

    async def send_order_driver(self, massage):
        """Send order details to the driver who accepted."""
        await self.send(text_data=json.dumps({
            "code": WS_SUCCESS,
            "action": "order",
            "data": massage,
        }))

    async def send_driver_user(self, massage):
        """Group send handler: notify client that a driver accepted their order."""
        await self.send(text_data=json.dumps({
            "code": WS_SUCCESS,
            "action": "driver",
            "data": massage["driver"],
        }))

    async def send_drivers(self, event):
        """Group send handler: push nearby driver list to client."""
        await self.send(text_data=json.dumps({
            "code": WS_SUCCESS,
            "action": "drivers",
            "data": event["message"],
        }))

    async def send_driver_location(self, event):
        """Group send handler: push real-time driver location to client."""
        await self.send(text_data=json.dumps({
            "code": WS_SUCCESS,
            "action": "driver_location",
            "data": event["message"],
        }))

    async def send_price(self, massage):
        """Send price calculation result to client."""
        await self.send(text_data=json.dumps({
            "code": WS_SUCCESS,
            "action": "price",
            "data": massage,
        }))

    async def chat_message(self, event):
        """Group send handler: chat message relay."""
        await self.send(text_data=json.dumps({
            "code": WS_SUCCESS,
            "action": "chat_message",
            "data": event["message"],
        }))

    async def send_to_group(self, orders, *args):
        for room_name in args:
            await self.channel_layer.group_send(
                room_name,
                {'type': 'chat_message', 'message': orders}
            )
