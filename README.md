# butterfly

### Version 2:
[![V2][V2.IMAGE.CI]][V2.LINK.CI] [![V2][V2.IMAGE.COVER]][V2.LINK.COVER]

[![V2][V2.IMAGE.CODACY]][V2.LINK.CODACY] [![V2][V2.IMAGE.QC]][V2.LINK.QC] 

### Master:
[![V1][V1.IMAGE.CI]][V1.LINK.CI]

[V2.IMAGE.CI]: https://img.shields.io/circleci/project/github/Rhoana/butterfly/update_v2.svg 
[V2.LINK.CI]: https://circleci.com/gh/Rhoana/butterfly/tree/update_v2
[V2.IMAGE.COVER]: https://img.shields.io/coveralls/Rhoana/butterfly/update_v2.svg
[V2.LINK.COVER]: https://coveralls.io/github/Rhoana/butterfly?branch=update_v2
[V2.IMAGE.QC]: https://www.quantifiedcode.com/api/v1/project/2ec68224940e403ab129befc98da67b0/snapshot/origin:update_v2:HEAD/badge.svg
[V2.LINK.QC]: https://www.quantifiedcode.com/app/project/2ec68224940e403ab129befc98da67b0?branch=origin%2Fupdate_v2
[V2.IMAGE.CODACY]: https://img.shields.io/codacy/grade/f8a7af03a553445ca1e53a673d2eff7d/update_v2.svg 
[V2.LINK.CODACY]: https://www.codacy.com/app/thejohnhoffer/butterfly/dashboard


[V1.IMAGE.CI]: https://img.shields.io/circleci/project/github/Rhoana/butterfly/master.svg 
[V1.LINK.CI]: https://circleci.com/gh/Rhoana/butterfly/tree/master


## Butterfly Installation

In your system shell, enter the below `code blocks` in order:

1. __Download__ and open the source code

    ```
    git clone https://github.com/Rhoana/butterfly.git
    cd butterfly
    ```

    - _Developers:_ Make and Open a virtualenv

2. __Prepare__ to install

    ```
    pip install -U 
    pip install -r requirements.txt
    ```

3. __Install__ `bfly` command

    ```
    pip install -e .
    ```

Now, you should be able to run the `bfly` command!

## Running Butterfly

Make sure `bfly --help` shows the below

```
usage: bfly [-h] [-e exp] [-o out] [port]

Butterfly Version 2.0

positional arguments:
  port               port >1024 for hosting this server (Default 2001)

optional arguments:
  -h, --help         show this help message and exit
  -e exp, --exp exp  path to load config yaml or folder with all data 
  -o out, --out out  path to save output yaml listing all --exp data
```

- If you simply run `bfly` without arguments,
    - The data loads from paths in `~/.rh-config.yaml`
    - The server starts on `http://localhost:2001`
- If you run `bfly 2017`,
    - The server starts on `http://localhost:2017`
- If you run `bfly -e ~/my-config.yaml`
    - The data loads from paths in `~/my-config.yaml`
- If your run `bfly -e ~/data -o ~/.rh-config.yaml`
    - The data loads from the `~/data` folder
    - The data paths save to `~/.rh-config.yaml`

## The RH Conifg (~/.rh-config.yaml)

The default path to this file is `~/.rh-config.yaml`
You can change this path by entering this to the shell:

```
export RH_CONFIG_FILENAME=~/my-config.yaml
```

After that, running `bfly` works like `bfly -e ~/my-config.yaml`

### The RH config file structure:


The __default values__ are given here:

```
bfly:
    # HTTP port to listen on
    port: 2001
    # Max size of the image cache in MB
    max-cache-size: 1024
    # Serve only files under a list of paths
    allowed-paths:
        - /
```

Let's say the user `username` has these folders in `~/data`:

- dense
    - excellent
        - synapse-segmentation.h5
        - neuron-segmentation.h5
    - synapse-training.h5
    - neuron-training.h5
    - raw-image.h5

This __must__ be mapped to a system _butterfly understands:_

- __experiment__ root
    - __sample__ data
        - __dataset__ excellent
            - __channel__ synapse-segmentation.h5
            - __channel__ neuron-segmentation.h5
        - __dataset__ dense
            - __channel__ synapse-training.h5
            - __channel__ neuron-training.h5
            - __channel__ raw-image.h5

The user `username` can save this mapping to `~/my-config.yaml` with this command:

```
bfly -e ~/data -o ~/my-config.yaml
```

Then, the user can edit `~/my-config.yaml` by hand to make `bfly` serve on port `2017` with up to 2 GiB of RAM used to cache images. The resulting `~/my-config.yaml` would then look like this:

```
bfly:
    port: 2001
    max-cache-size: 2048
    experiments:
        - name: root
          samples:
            - name: data
                datasets:
                    - name: dense
                      channels:
                          - name: neuron-training.h5
                            path: /home/username/data/dense/neuron-training.h5
                          - name: raw-image.h5
                            path: /home/username/data/dense/raw-image.h5
                          - name: synapse-training.h5
                            path: /home/username/data/dense/synapse-training.h5
                    - path: /home/username/data/dense
                    - name: excellent
                      channels:
                          - name: neuron-segmentation.h5
                            path: /home/username/data/dense/excellent/neuron-segmentation.h5
                          - name: synapse-segmentation.h5
                            path: /home/username/data/dense/excellent/synapse-segmentation.h5
                    - path: /home/username/data/dense/excellent
```

Finally, this file at `/home/username/my-config.yaml` will be used by default whenever the `bfly` command is run so long as `username` remembers to type this in their shell:

```
export RH_CONFIG_FILENAME=~/my-config.yaml
```
