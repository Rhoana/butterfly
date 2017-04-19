import numpy as np
import json

def flatten(output, item):
    if 'path' in item:
        return output + [item]
    if not isinstance(item, dict):
        return output
    return reduce(flatten, item.values(), output)

def values(res, key, nest=[], **keywords):
    name = '{}_{}_{}'.format(*key)
    # Format the nested paths
    paths = '/'.join(nest)
    # add values to dictionary
    if 'path' in keywords:
        fmt = keywords['path']
        # Add the full formatted path
        full = fmt.format(paths, *key)
        keywords['path'] = full
        # Add the position list
        keywords['nest'] = nest + [name]
    # add to parent dictionary
    res[name] = keywords

def add(res, keys, nest=[], **keywords):
    targets = res.keys()
    if not targets:
        for key in keys:
            # add values to this level
            values(res, key, nest, **keywords)
    else:
        for target in targets:
            # Add to the list of nest levels
            nested = nest + [target]
            # add next levels to this level
            add(res[target], keys, nested, **keywords)

def add_all(result, shape, **keywords):
    # Add all possible keys at this level
    all_keys = np.where(np.ones(shape))
    add(result, zip(*all_keys), **keywords)
    # Get the result
    return result


def nester(tile_shape, group_shapes):

    result = {}
    file_fmt = 'data/{0}/raw_{1:04d}_{2:04d}_{3:04d}.h5'

    # Add all the folder levels
    for shape in group_shapes:
        result = add_all(result, shape)
    # Add all the tile endpoints
    result = add_all(result, tile_shape, path=file_fmt)

    # Get full result
    return result

class Simplifier():
    def __init__(self, nesting):
        self.nesting = nesting

    def simplify(self, item):
        nests = [n.split('_') for n in item['nest']]
        offset = (self.nesting * np.uint32(nests)).sum(0)
        return {
            'path': item['path'],
            'offset': list(offset),
        }

def main(out_file, tile_shape, group_shapes):
    # Get file path structures
    nested = nester(tile_shape, group_shapes)
    listed = reduce(flatten, nested.values(), [])

    # Get the sizes for each nesting
    levels = [tile_shape] + group_shapes[:-1]
    # Get the cumulative effect of each layer
    nesting = np.cumprod(levels, axis=0)
    nesting = np.r_[nesting[::-1], [[1,1,1]]]
    # Simplify
    simp = Simplifier(nesting)
    output = map(simp.simplify, listed)

    # Document the model
    with open(out_file,'w') as fd:
        json.dump(output, fd, indent=4)

if __name__ == '__main__':
    out_file = 'dataset.json'
    tile_shape = [10,10,10]
    group_shapes = [
        [2,2,2],
    ]
    main(out_file, tile_shape, group_shapes)

