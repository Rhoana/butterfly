# Root layers
import QueryLayer

# Get all classes
from API import API
from OCP import OCP
from StaticHandler import StaticHandler
from RequestHandler import RequestHandler

# Take all layers from QueryLayer
from QueryLayer import UtilityLayer
from QueryLayer import ImageLayer

# Define all classes in AccessLayer
__all__ = ['API', 'OCP']
__all__ += ['StaticHandler', 'RequestHandler']
# Define all the layers in AccessLayer
__all__ += ['QueryLayer']
__all__ += ['UtilityLayer', 'ImageLayer']
