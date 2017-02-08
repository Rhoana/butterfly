class Query(object):
    raw = dict()
    basic = {
        'format': 'png',
        'feature': 'data',
        'view': 'grayscale',
    }
    def __init__(self,**kwargs):
        methods = ['feature','format','view','id']
        groups = ['experiment','sample','dataset','channel']
        box = ['x','y','z','height','width','depth','resolution']
        allkeys = ['datapath'] + box + groups + methods
        rawlist = [k for k in allkeys if k in kwargs]
        for key in rawlist:
            self.raw[key] = kwargs[key]
