class Image_ID(object):
    def __init__(self, query, xy_index):

        self.z = query.z
        self.y = xy_index[0]
        self.x = xy_index[1]
        self.w = query.scale

        self.datapath = query.datapath
        self.blocksize = query.blocksize
        self.disk_format = query.disk_format

    @property
    def key(self):
        return '_'.join(self.wxyz)

    @property
    def wxyz(self):
        return np.array([self.w, self.x, self.y, self.z])

