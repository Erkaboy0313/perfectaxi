# Web socket url

wss://api.perfecttaxi.uz/ws/order/default/

# Narxlarni olish

{
    "command":"calculate_price",
    "start_point":"69.253287,41.311190",
    "points":["69.284654,41.336120","69.253709,41.311296"], # optional
    "service":[] #optional
}

# Natija

{
    "action": "price",
    "message": [
        {
            "id": 1,
            "service": "standart",
            "cost": 11640.0
        },
        {
            "id": 2,
            "service": "bussiness",
            "cost": 14360.0
        },
        {
            "id": 3,
            "service": "comfort",
            "cost": 22400.0
        }
    ]
}


# Buyurtma berish

{
    "command":"new_order",
    "start_point":"69.253287,41.311190",
    "points":["69.284654,41.336120","69.253709,41.311296"],
    "carservice":1,
    "price":11640.0,
    "services":[]
}

# Natija

{
    "action": "order",
    "message": {
        "id": 15,
        "point_set": [
            {
                "point": "69.284654,41.336120"
            },
            {
                "point": "69.253709,41.311296"
            }
        ],
        "contact_number": "+998937874663",
        "start_adress": null,
        "start_point": "69.253287,41.311190",
        "ordered_time": "21-08-2023 10:18",
        "taken_time": null,
        "rejected_time": null,
        "distance": null,
        "price": 11640.0,
        "payment_type": "cash",
        "status": "active",
        "reject_reason": null,
        "client": 4,
        "driver": null,
        "carservice": 1,
        "services": []
    }
}