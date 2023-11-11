from geopy import distance


def caculateDistance(start,points=[]):
    def convert2tuple(cor):
        return [float(x) for x in cor.split(',')]
    cordinates = list(map(convert2tuple,points))
    cordinates.insert(0,convert2tuple(start))
    if len(cordinates) > 1:
        d = distance.distance(*cordinates)
        return round(d.km,1)
    else:
        return 0
    