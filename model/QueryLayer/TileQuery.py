from Query import Query

class TileQuery(Query):

    def __init__(self, *args, **kwargs):

        query,xy_index = args
        self.X,self.Y,self.Z = self.position[:3]
        self.W,self.H,self.R = self.position[3:]
        self.make_getter('tile_keys', '')
        self.make_getter('data_keys', '')
        self.make_getter('position', -1)
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
        rhwxyz = map(self.att,map(self.att,'RHWXYZ'))
        return '_'.join(map(str,rhwxyz))
