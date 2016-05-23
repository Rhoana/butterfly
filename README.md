# butterfly

## Requirements
- Requires OpenCV 2.4+
- Python requirements in [requirements.txt](requirements.txt)

## Installation
```bash
$ git clone https://github.com/Rhoana/butterfly.git
$ pip install -e .
```

## Usage
NOTE: Default port is currently 2001
```bash
$ bfly [<port>]
```

### bfly configuration

bfly uses rh_config which gets its configuration by default from
~/.rh-config.yaml. You can change this by setting the environment variable,
RH_CONFIG_FILENAME, to the name of the config file you want to use. bfly
uses two configuration sections, "bfly" and "rh_logger" (rh_logger is
documented here: https://github.com/rhoana/rh_logger). The bfly section
has the following structure:

    bfly:
        # data sources to try in order of their appearance
        #
        datasource:
            - comprimato
            - multibeam
            - mojo
            - regularimagestack
        # HTTP port to listen on
        port: 2001
        # size of the image cache to maintain in MB
        max-cache-size: 1000
        assent-list:
            - yes
            - y
            - true
        always-subsample: True
        #
        # Interpolation method - one of linear, area, nearest or cubic
        #
        image-resize-method: linear
        # Paths to the section files must start with one of the following:
        allowed-paths:
            - /data
        # Suppress tornado logging (was SUPPRESS_CONSOLE_OUTPUT)
        suppress-tornado-logging: True

## P3 Args
TODO: document P3 args (maybe?):
```
--filename %(z)04d_Tile_r1-c1_W02_sec%(z)03d_tr%(y)d-tc%(x)d_.png
--folderpaths %(z)04d_Tile_r1-c1_W02_sec%(z)03d
--x_ind 1-3
--y_ind 1-4
--z_ind 1-3
--blocksize 16384 16384
```

## AC3 Args
TODO: document ac3 args (maybe?):
```
--filename y=%(y)08d,x=%(x)08d.tif
--folderpaths z=%(z)08d
--x_ind 0 1
--y_ind 0 1
--z_ind 0-74
--blocksize 512 512
```

