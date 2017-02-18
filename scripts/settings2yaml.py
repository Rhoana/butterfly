import yaml
from Settings import *
data = {
    'INPUT': INPUT(),
    'RUNTIME': RUNTIME(),
    'OUTPUT': OUTPUT()
}
with open('Settings.yaml', 'w') as outfile:
    yaml.dump(data, outfile, default_flow_style=False)


    