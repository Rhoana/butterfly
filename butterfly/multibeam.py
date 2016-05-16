from datasource import DataSource


class MultiBeam(DataSource):

    def __init__(self, core, datapath):
        '''
        @override
        '''

        super(MultiBeam, self).__init__(core, datapath)

    def index(self):
        '''
        @override
        '''

        super(MultiBeam, self).index()

    def load(self, x, y, z, w, segmentation=False):
        '''
        @override
        '''

        cur_path = None

        return super(MultiBeam, self).load(cur_path, w, segmentation)

    def seg_to_color(self, slice):
        # super(MultiBeam, self).seg_to_color()

        return slice

    def get_boundaries(self):
        # super(MultiBeam, self).get_boundaries()

        pass
