from utils.cache_functions import getKeys,getKey



def findCloseDriver(location = None,order= None):
    # should find available and closest drivers
    
    online_drivers = getKeys('DL_*')
    blacklist = getKey(f'b{order}')
    drivers = [getKey(x) for x in online_drivers]

    if blacklist:
        return [x for x in drivers if x not in blacklist]
    else:
        return drivers