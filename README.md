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
