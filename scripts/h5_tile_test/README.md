## Setting the parameters

Set an environment variable for the name of the experiment
```
export H5_EXPERIMENT='experiment_94'
```

In `record_data.py`
    - The `full_shape` should be the total `[z, y, x]` volume to test.
    - The `file_divs` should list ways to divide that volume across files.
    - The `tile_sizes` should list partial shapes used to load the full volume.

## Running the batch job

```
sbatch --array=0-19 h5_tile_test.sbatch
```
