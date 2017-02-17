from Query import Query

class TileQuery(Query):

    def __init__(self, *args, **kwargs):

        query,xy_index,start,end = args
        self.R = self.SPACE_LIST[5]
        self.I,self.J = self.TILE_LIST[:2]
        self.X,self.Y,self.Z = self.SPACE_LIST[:3]
        self.make_getter('TILE_LIST', '')
        self.make_getter('DATA_LIST', '')
        self.make_getter('SPACE_LIST', -1)
        self.raw = {
            self.X: xy_index[1],
            self.Y: xy_index[0],
            self.I: [start[0],end[0]],
            self.J: [start[1],end[1]]
        }
        for k in ['PATH','BLOCK','DISK','R','Z']:
            term = getattr(self,k)
            self.raw[term] = getattr(query,term)

    @property
    def key(self):
        rhwxyz = map(self.getatt,'RIJXYZ')
        return '_'.join(map(str,rhwxyz))
