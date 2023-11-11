COORDINATES = [
    (41.311081, 69.240562),
    (41.299495, 69.284904),
    (41.292485, 69.264046),
    (41.307843, 69.290537),
    (41.311670, 69.255178),
    (41.313899, 69.273712),
    (41.306408, 69.276995),
    (41.305158, 69.248835),
    (41.308271, 69.263990),
    (41.299951, 69.266434),
    (41.304512, 69.289765),
    (41.300815, 69.278686),
    (41.303104, 69.271974),
    (41.308653, 69.269066),
    (41.307354, 69.285211),
    (41.310232, 69.284246),
    (41.302543, 69.249850),
    (41.310350, 69.250581),
    (41.312857, 69.283150),
    (41.308441, 69.249165),
    (41.301426, 69.254303),
    (41.306509, 69.286201),
    (41.299688, 69.275080),
    (41.299196, 69.281463),
    (41.300485, 69.285450),
    (41.303679, 69.280454),
    (41.309108, 69.274915),
    (41.308984, 69.247148),
    (41.298221, 69.253242),
    (41.307124, 69.249341),
    (41.306980, 69.264198),
    (41.302983, 69.287764),
    (41.309305, 69.271521),
    (41.301875, 69.285634),
    (41.299631, 69.278773),
    (41.310841, 69.266620),
    (41.300582, 69.279660),
    (41.301755, 69.262847),
    (41.300153, 69.287456),
    (41.298819, 69.273536),
    (41.303930, 69.266232),
    (41.304651, 69.247949),
    (41.299719, 69.273184),
    (41.305222, 69.262340),
    (41.308696, 69.288112),
    (41.302319, 69.287862),
    (41.305079, 69.249534),
    (41.311856, 69.256479),
    (41.303175, 69.287340),
    (41.304608, 69.275660),
    (41.303151, 69.269447),
    (41.301225, 69.260415),
    (41.307244, 69.270262),
    (41.305358, 69.275138),
    (41.299799, 69.252930),
    (41.300688, 69.259414),
    (41.300717, 69.258964),
    (41.309590, 69.276548),
    (41.298631, 69.285601),
    (41.305389, 69.283760),
    (41.309710, 69.268143),
    (41.306848, 69.279964),
    (41.299112, 69.260979),
    (41.305248, 69.280275),
    (41.300771, 69.271439),
    (41.309133, 69.271266),
    (41.299580, 69.284360),
    (41.308109, 69.265453),
    (41.301430, 69.278000),
    (41.308946, 69.254407),
    (41.301266, 69.282416),
    (41.298859, 69.284619),
    (41.306313, 69.288582),
    (41.309385, 69.264889),
    (41.302789, 69.282552),
    (41.309096, 69.260824),
    (41.301584, 69.253053),
    (41.307450, 69.284670),
    (41.305448, 69.264590),
    (41.308826, 69.252784),
    (41.310090, 69.261032),
    (41.303759, 69.252645),
    (41.304305, 69.267304),
    (41.303715, 69.283956),
    (41.304563, 69.251578),
    (41.305172, 69.266052),
    (41.308926, 69.285248),
    (41.305661, 69.270046),
    (41.306420, 69.282091),
    (41.303912, 69.260088),
    (41.302576, 69.278971),
    (41.303477, 69.280232),
    (41.306949, 69.249413),
    (41.309133, 69.264580),
    (41.306258, 69.249998),
    (41.310936, 69.263335),
    (41.308441, 69.265138),
    (41.309385, 69.271425),
    (41.307274, 69.280732),
    (41.302074, 69.255708),
    (41.300312, 69.258610),
    (41.306276, 69.265949),
    (41.307112, 69.257199),
    (41.300695, 69.275089),
    (41.303472, 69.269706),
    (41.309756, 69.271788),
    (41.307960, 69.250478),
    (41.306202, 69.263072),
    (41.310036, 69.265608),
    (41.299534, 69.282563),
    (41.310616, 69.270946),
    (41.303871, 69.267422),
    (41.299875, 69.252667),
    (41.307757, 69.250390),
    (41.299764, 69.271365),
    (41.300200, 69.255464),
    (41.304609, 69.280787),
    (41.304817, 69.275689),
    (41.300955, 69.274150),
    (41.300332, 69.250725),
    (41.309502, 69.269170),
    (41.308465, 69.271657),
    (41.307556, 69.274147),
    (41.310147, 69.276663),
    (41.303152, 69.251763),
]
import redis
import requests
import json
from utils.calculateDistance import caculateDistance
import os
redis_client = redis.Redis(host=os.environ.get('REDIS_HOST'), port=6379, db=0)


class FindRoute:
    def __init__(self):
        self.__BASE_URL = 'http://router.project-osrm.org/'
        self.__MATRIX = 'table/v1/driving/'
        self.__ROUTE = 'route/v1/driving/'

    def find_drive(self,start,points):
        def reverse(point):
            long,lat = point.split(',')
            res = f"{lat},{long}"
            return res.strip()
        if points:
            cordinate = reverse(start)
            cordinate += ";"+(';'.join(list(map(reverse,points))))
            url = self.__BASE_URL + self.__ROUTE + cordinate
            response = requests.get(url)
            if response.status_code == 200:
                data = json.loads(response.text)
                return data['routes'][0]['distance'] / 1000
            else:
                return caculateDistance(start,points)
        else:
            return 0

    def find_route(self,source,destination):
        
        sources = []
        for driver in source:
            sources.append(f"{driver[2][0]},{driver[2][1]}")
        indexes = ';'.join(list(map(str,list(range(len(sources))))))
        source = ';'.join(sources)

        coordinate = f"{source};{destination}?sources={indexes}&destinations={len(sources)}"
        respose = requests.get(self.__BASE_URL+self.__MATRIX+coordinate)
        data = json.loads(respose.text)
        if respose.status_code == 200:
            return data['durations']
        else:
            return False
        
def update_driver_location(driver_id, longitude, latitude):
    redis_client.geoadd('driver_locations',(longitude,latitude,driver_id))

def find_nearest_drivers(longitude, latitude, radius, count):
    result = redis_client.georadius('driver_locations', longitude, latitude, radius, unit='m', withdist=True, withcoord=True, count=count, sort='ASC')
    return result

def remove_location(id):
    redis_client.zrem("driver_locations",id)

def retrieve_location(id):
    return redis_client.geopos('driver_locations',id)[0]

def PopulateLocations():
    for id,location in enumerate(COORDINATES):
        update_driver_location(id,location[1],location[0])
    else:
        print("populated")


route = FindRoute()
route.find_drive('41.286384, 69.227279',['41.296296, 69.216240','41.260209, 69.197470'])

