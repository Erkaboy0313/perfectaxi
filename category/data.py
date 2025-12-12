from .models import CarBrend, CarModel, Color, CarService



def seed_data():

    CarService.objects.all().delete()
    CarBrend.objects.all().delete()
    CarModel.objects.all().delete()
    Color.objects.all().delete()

    # -----------------------
    # 1. Car brands
    # -----------------------
    brands = [
        "Toyota", "Honda", "Hyundai", "Kia", "Chevrolet",
        "Mercedes-Benz", "BMW", "Audi", "Volkswagen",
        "Lexus", "Ford"
    ]

    brand_objects = {}
    for b in brands:
        obj, _ = CarBrend.objects.get_or_create(name=b)
        brand_objects[b] = obj

    # -----------------------
    # 2. Car models
    # -----------------------
    models = {
        "Toyota": ["Camry", "Corolla", "Prius"],
        "Honda": ["Civic", "Accord"],
        "Hyundai": ["Elantra", "Sonata"],
        "Kia": ["K5", "Rio", "Optima"],
        "Chevrolet": ["Cobalt", "Nexia 3", "Malibu"],
        "Mercedes-Benz": ["E-Class", "S-Class"],
        "BMW": ["5 Series", "7 Series"],
        "Audi": ["A4", "A6"],
        "Volkswagen": ["Passat", "Polo"],
        "Lexus": ["ES 350", "RX 350"],
        "Ford": ["Focus", "Mondeo"]
    }

    for brand_name, model_list in models.items():
        for m in model_list:
            CarModel.objects.get_or_create(
                brend=brand_objects[brand_name],
                name=m
            )

    # -----------------------
    # 3. Colors
    # -----------------------
    colors = ["White", "Black", "Silver", "Gray", "Blue", "Red", "Brown"]

    for c in colors:
        Color.objects.get_or_create(name=c)

    # -----------------------
    # 4. Services
    # -----------------------
    services = [
        {
            "service": "standart",
            "includedCars": "Cobalt,Nexia 3,Rio,Elantra",
            "start_price": 7000,
            "price_per_km": 1500,
            "price_per_min": 200,
            "wait_price_per_min": 150,
            "free_wait_time": 3,
        },
        {
            "service": "comfort",
            "includedCars": "Camry,Sonata,K5",
            "start_price": 9000,
            "price_per_km": 2200,
            "price_per_min": 350,
            "wait_price_per_min": 200,
            "free_wait_time": 5,
        },
        {
            "service": "bussiness",
            "includedCars": "E-Class,5 Series,A6",
            "start_price": 15000,
            "price_per_km": 3500,
            "price_per_min": 500,
            "wait_price_per_min": 300,
            "free_wait_time": 7,
        },
    ]

    for s in services:
        CarService.objects.get_or_create(service=s["service"], defaults=s)

    print("✅ Database seeded successfully!")
