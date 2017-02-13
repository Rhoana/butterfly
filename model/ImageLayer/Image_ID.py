class Image_ID(object):
    def __init__(self, xy_index, depth, scale):
        self.x_index = xy_index[1]
        self.y_index = xy_index[0]
        self.z_index = depth
        self.scale = scale
