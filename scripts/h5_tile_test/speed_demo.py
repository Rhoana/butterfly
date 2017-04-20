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

def make_one(shapes, full_shape):
    if os.path.exists('data'):
        shutil.rmtree('data')
    tile_shape, group_shape = shapes
    out_file = get_filename(tile_shape, group_shape)
    make_nested.main(out_file, tile_shape, [group_shape])
    return test_nested.do_make(out_file, full_shape)

def test_one(trials, model, full_shape, tile_shape, file_block):
    args = trials, model, full_shape, tile_shape, file_block
    return test_nested.do_test(*args)

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

    trials = 20
    #full_shape = [16, 16384, 16384]
    full_shape = [2048, 16384, 16384]
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
    ][::-1]
    speeds = []
    # Make and test hdf5 files
    for t_g in tile_group_shapes:

        # Prepare and make an h5 file
        t_s, model = make_one(t_g, full_shape)
        print t_s
        for f_b in file_blocks:
            # Set a max cutoff at 1024 blocks
            n_blocks = np.prod(f_b * np.multiply(*t_g))
            if n_blocks > 1024:
                continue
            # Get the speed for the requested sizes
            speed = test_one(trials, model, full_shape, t_s, f_b)
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

