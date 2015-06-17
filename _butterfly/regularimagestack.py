from datasource import Datasource

class RegularImageStack(Datasource):
  
  def __init__(self, datapath):
    '''
    @override
    '''

    super(RegularImageStack, self).__init__(datapath)

  def index(self):
    '''
    @override
    '''

    super(RegularImageStack, self).index()
