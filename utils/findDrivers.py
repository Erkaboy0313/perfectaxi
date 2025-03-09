from utils.cordinates import find_nearest_drivers,FindRoute
from utils.cache_functions import sgetKey
from users.models import Driver
import asyncio
from category.models import Log

def serializeCloseDriver(drivers_list,service):
    drivers = []
    for driver in drivers_list:
        d = Driver.objects.get(user__id = int(driver[0]))
        services = d.avilable_service.filter(on = True)
        if service and services.filter(service__service = service).exists():
            driver_obj = {
                'id':int(driver[0]),
                'c_loc':{"latitude":driver[2][1],
                        "longitude":driver[2][0]},
                'p_loc':{"latitude":float(sgetKey(f"prev_loc_{int(driver[0])}").split(",")[0]),
                        "longitude":float(sgetKey(f"prev_loc_{int(driver[0])}").split(",")[1])},
                'service':service
            }
            drivers.append(driver_obj)
        elif not service:
            driver_obj = {
                'id':int(driver[0]),
                'c_loc':{"latitude":driver[2][1],
                        "longitude":driver[2][0]},
                'p_loc':{"latitude":float(sgetKey(f"prev_loc_{int(driver[0])}").split(",")[0]),
                        "longitude":float(sgetKey(f"prev_loc_{int(driver[0])}").split(",")[1])},
                'service':services.first().service.service
            }
            drivers.append(driver_obj)
    return drivers

def serializeAvailableDriver(drivers_list):
    drivers = []
    for driver in drivers_list:
        driver_obj = {
            'id':int(driver[0]),
            'c_loc':{"latitude":driver[2][1],
                    "longitude":driver[2][0]},
            'p_loc':{"latitude":float(sgetKey(f"prev_loc_{int(driver[0])}").split(",")[0]),
                    "longitude":float(sgetKey(f"prev_loc_{int(driver[0])}").split(",")[1])},
            'mark':driver[3],
            'distance':driver[4],
            'time':driver[5]
        }
        drivers.append(driver_obj)
    return drivers

def findCloseDriver(location = None,radius:int = 1000,service:str = 'standart'):
    long,lat = tuple(map(float,location.split(',')))
    drivers = find_nearest_drivers(lat,long,radius,10)
    return serializeCloseDriver(drivers,service)

def findAvailableDrivers(location,radius,order_id,service):
    black_list = sgetKey(f"black_list_{order_id}")
    black_list = black_list if black_list else []
    #Find nearest drivers
    long,lat = tuple(map(float,location.split(',')))
    drivers = find_nearest_drivers(lat,long,radius,10)
    Log.objects.create(text = f'{order_id} drrr: {black_list}: Topilgan driverlar {drivers[0] if drivers else drivers}')
    #Filter by black list
    if black_list:
        drivers = filter(lambda x: not int(x[0]) in black_list,drivers)
        
    #Filter by service
    available_drivers = []
    for i in drivers:
        driver = Driver.objects.get(user__id = int(i[0]))
        if driver.avilable_service.filter(service__service = service,on = True).exists():
            i.append(driver.mark)
            available_drivers.append(i)
        else:
            black_list.append(int(i[0]))
            
    #Order by distance and mark
    return OrderDriversByRoute(available_drivers,location)

def OrderDriversByRoute(drivers,destination):
    
    for driver in drivers:
        data = asyncio.run(FindRoute().find_distance_time(f"{driver[2][1]},{driver[2][0]}",destination))
        if data:
            driver += data
    # return Serialized Data
    return serializeAvailableDriver(list(sorted(drivers,key=lambda x:(-x[3], x[4]))))
    