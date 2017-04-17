import make_nested
import test_nested
import numpy as np
import shutil
import json
import os

def get_filename(tile_shape, group_shape):
    t_n = np.prod(tile_shape)
    g_n = np.prod(group_shape)
    return '{}_in_{}.json'.format(t_n, g_n)

def make_one(shapes):
    tile_shape, group_shape = shapes
    out_file = get_filename(tile_shape, group_shape)
    return make_nested.main(out_file, tile_shape, [group_shape])

def test_one(shapes, trials, full_shape, file_block):
    if os.path.exists('data'):
        shutil.rmtree('data')
    tile_shape, group_shape = shapes
    in_file = get_filename(tile_shape, group_shape)
    return test_nested.main(in_file, trials, full_shape, file_block)

if __name__ == '__main__':
    tile_group_shapes = [
#       [ [1,1,1], [2,2,2] ],
#       [ [2,2,2], [2,2,2] ],
#       [ [4,4,4], [2,2,2] ],
       [ [1,1,1], [1,1,1] ],
       [ [1,1,2], [1,1,1] ],
       [ [1,2,2], [1,1,1] ],
       [ [1,2,4], [1,1,1] ],
       [ [1,4,4], [1,1,1] ],
#       [ [8,8,8], [1,1,1] ],
    ]

    # Make both json files
    map(make_one, tile_group_shapes)

    trials = 2
    full_shape = [8, 8192, 8192]
    file_blocks = [
        [1, 1, 1],
        [1, 1, 2],
        [1, 2, 2],
        [1, 2, 4],
        [1, 4, 4],
        [1, 4, 8],
        [1, 8, 8],
        [1, 16, 8],
        [1, 16, 16],
        [1, 32, 16],
        [1, 32, 32],
    ]
    speeds = []
    # Make and test hdf5 files
    for t_g in tile_group_shapes:
        for f_b in file_blocks:
            # Set a max cutoff at 1024 blocks
            n_blocks = np.prod(f_b * np.multiply(*t_g))
            if n_blocks > 1024:
                continue
            # Get the speed for the requested sizes
            speed = test_one(t_g, trials, full_shape, f_b)
            if not speed:
                continue
            speed.update({
                'n_folders': t_g[1],
                'n_trials': trials,
            })
            speeds.append(speed)
            msg = """
mean of {n_trials} trials: {mean_time} for
    {n_tiles_kji} tiles from {n_files_zyx} files
    over {n_folders} folders.""".format(**speed)
            print(msg)

    # Document the model
    speed_fmt = 'speed_{}_{}_{}.json'
    speed_out = speed_fmt.format(*full_shape)
    # Write the model to json
    with open(speed_out, 'w') as fd:
        json.dump(speeds, fd, indent=4)

