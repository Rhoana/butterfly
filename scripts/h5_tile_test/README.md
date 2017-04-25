## Setting the parameters

In `graph_data.py` and `record_data.py`, the `graph_dir` should be the same. 
In `record_data.py`
    - The `full_shape` should be the total `[z, y, x]` volume to test.
    - The `file_divs` should list ways to divide that volume across files.
    - The `tile_sizes` should list partial shapes used to load the full volume.

## Running the batch job

The array should be the same length as the `len(file_divs)*len(tile_sizes)`

```
sbatch --array=0-7 record_data.sbatch
```
