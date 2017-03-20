# Root layer
import CoreLayer

# Get all classes
from Webserver import Webserver
from Butterfly import Butterfly

# Take all layers from CoreLayer
from CoreLayer import AccessLayer
from CoreLayer import QueryLayer
from CoreLayer import ImageLayer
from CoreLayer import UtilityLayer
from CoreLayer import DatabaseLayer

# Define all modules of bfly
__all__ = ["Butterfly", "Webserver"]
# Define all the layers in bfly
__all__ += ["CoreLayer", "DatabaseLayer"]
__all__ += ["UtilityLayer", "ImageLayer"]
__all__ += ["QueryLayer", "AccessLayer"]

