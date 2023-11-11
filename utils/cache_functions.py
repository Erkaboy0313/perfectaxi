from django.core.cache import cache



# This function increase value by one
def incrKey(key, value, timeout=None):
    return cache.incr(key, delta=value)

def removeKey(key):
    return cache.delete(key)

# This function set value
def setKey(key, value, timeout=None):
    return cache.set(key, value, timeout=timeout)

# This function set value if key exist then give error
def addKey(key, value, timeout=None):
    return cache.add(key, value, timeout=timeout)

# this function get value by key
def getKey(key):
    return cache.get(key)

def getKeys(key):
    return cache.keys(key)


