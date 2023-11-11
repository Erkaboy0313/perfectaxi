from utils.cordinates import find_nearest_drivers,FindRoute

def findCloseDriver(location = None):
    long,lat = tuple(map(float,location.split(',')))
    drivers = find_nearest_drivers(lat,long,2000,10)
    return drivers

def OrderDriversByRoute(drivers,destination):
    long,lat = tuple(map(float,destination.split(',')))
    route = FindRoute()
    times = route.find_route(drivers,f"{lat},{long}")
    if times:
        for i in range(len(drivers)):
            drivers[i].append(times[i])
        return list(sorted(drivers,key=lambda x: x[3]))
    return drivers