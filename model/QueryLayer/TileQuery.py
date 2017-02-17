from Query import Query

class TileQuery(Query):

    def __init__(self, *args, **kwargs):

        query,xy_index = args
        self.X,self.Y,self.Z = self.SPACE_LIST[:3]
        self.W,self.H,self.R = self.SPACE_LIST[3:]
        self.make_getter('TILE_LIST', '')
        self.make_getter('DATA_LIST', '')
        self.make_getter('SPACE_LIST', -1)
        self.raw = {
            self.X: xy_index[1],
            self.Y: xy_index[0],
            self.W: 512,
            self.H: 512
        }
        for k in ['PATH','BLOCK','DISK','Z','R']:
            term = getattr(self,k)
            self.raw[term] = getattr(query,term)

    @property
    def key(self):
        rhwxyz = map(self.getatt,'RHWXYZ')
        return '_'.join(map(str,rhwxyz))
