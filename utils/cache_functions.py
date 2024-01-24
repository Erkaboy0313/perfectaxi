from django.core.cache import cache



# This function increase value by one
async def incrKey(key, value, timeout=None):
    return cache.incr(key, delta=value)

async def removeKey(key):
    return cache.delete(key)

def sremoveKey(key):
    return cache.delete(key)

# This function set value
async def setKey(key, value, timeout=None):
    return cache.set(key, value, timeout=timeout)

def ssetKey(key, value, timeout=None):
    return cache.set(key, value, timeout=timeout)

# This function set value if key exist then give error
async def addKey(key, value, timeout=None):
    return cache.add(key, value, timeout=timeout)

# this function get value by key
async def getKey(key):
    return cache.get(key)

def sgetKey(key):
    return cache.get(key)

async def getKeys(key):
    return cache.keys(key)


