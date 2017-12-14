import logging as log
from scipy.sparse import lil_matrix
import numpy as np
import scipy
import sys
import os

TYPES = [
    scipy.sparse.lil.lil_matrix,
]
SPLIT_EXT = ".split.npy"
SPLIT_DAT = 7
MERGE_EXT = ".merge.npy"
MERGE_DAT = 2

def get_merge_file(path):
    """ Concat MERGE_EXT to a filenmae
    
    Arguments
    ----------
    path: str
        The path to a whole datasource volume

    Returns
    --------
    str
       The filename for all merges

    """
    return path.rstrip(os.sep)+MERGE_EXT
    
def get_split_file(path):
    """ Concat SPLIT_EXT to a filenmae
    
    Arguments
    ----------
    path: str
        The path to a whole datasource volume

    Returns
    --------
    str
       The filename for all splits

    """
    return path.rstrip(os.sep)+SPLIT_EXT
 
def count_bytes(v):
    """ Count bytes in sparse matrix
    
    Arguments
    ----------
    v: lil_matrix

    Returns
    ---------
    int
        Number of bytes in v
    """
    d_bytes = v.nnz * (v.data.nbytes + v.rows.nbytes)
    p_bytes = sys.getsizeof(v)
    return d_bytes + p_bytes

#######
# Input and Generation
#######
def make_sparse_mt(id_gen):
    """ Make a sparse merge matrix of max length

    Arguments
    ----------
    id_gen : generator
        yields [key, root, region] per merge

    Returns
    --------
    lil_matrix
        Vector of all 64-bit unsigned ints
    """
    T_SHAPE = (MERGE_DAT, sys.maxsize)
    t_merge = lil_matrix(T_SHAPE, dtype=np.int64)
    # Add each id item to matrix
    for merge_dat in id_gen:
        key = merge_dat[0]
        # Map main key to root and region
        for i in range(MERGE_DAT):
            t_merge[i, key] = merge_dat[i + 1]
    return t_merge

def make_sparse_st(id_gen):
    """ Make a sparse split matrix of max length

    Arguments
    ----------
    id_gen : generator
        yields [region, key, x0, x1, y0, y1, z0, z1] per split

    Returns
    --------
    lil_matrix
        Vector of all 64-bit unsigned ints
    """
    T_SHAPE = (SPLIT_DAT, sys.maxsize)
    t_split = lil_matrix(T_SHAPE, dtype=np.int64)
    # Add each id item to matrix
    for split_dat in id_gen:
        region = split_dat[0]
        # Map region to main key and bounds
        for i in range(SPLIT_DAT):
            t_split[i, region] = split_dat[i + 1]
    return t_split

def load_mt(path):
    """ Read sparse matrix in merge file

    Arguments
    -----------
    path: str
        The path to a whole datasource volume

    Returns
    ---------
    lil_matrix
        The current merges
    """
    merge_path = get_merge_file(path)
    if not os.path.exists(merge_path):
        return make_sparse_mt(iter(()))
    saved_merges = np.load(merge_path, mmap_mode='r')
    return make_sparse_mt(iter(saved_merges))

def load_st(path):
    """ Read sparse matrix in split file

    Arguments
    -----------
    path: str
        The path to a whole datasource volume

    Returns
    ---------
    lil_matrix
        The current merges
    """
    split_path = get_split_file(path)
    if not os.path.exists(split_path):
        return make_sparse_st(iter(()))
    saved_splits = np.load(split_path, mmap_mode='r')
    return make_sparse_st(iter(saved_splits))

def to_sparse_mt(sv_new):
    """ Make a sparse merge table from disjoint sets

    Arguments
    ----------
    sv_new: [[str]]
        List of all merged lists of ids

    Returns
    --------
    lil_matrix
        The new merges
    """
    def read_id(root, merge):
        key, region = (merge+':0').split(':')[:MERGE_DAT]
        return np.uint64([key, root, region]) + 1

    # Key ID, Root ID, and region
    id_gen = (read_id(m[0], i) for m in sv_new for i in m)
    # Make new sparse merge table
    return make_sparse_mt(id_gen)

def to_sparse_st(sv_new):
    """ Make a sparse split table from list of splits

    Arguments
    ----------
    sv_new: [[str]]
        List of all split subregions

    Returns
    --------
    lil_matrix
        The new splits
    """
    def read_id(split):
        dat = tuple(split.split(':')[:SPLIT_DAT+1])
        # Swap the first two items
        split_dat = dat[1::-1] + dat[2:]
        return np.uint64(split_dat) + 1

    # Key ID, Root ID, and region
    id_gen = (read_id(s) for s in sv_new)
    # Make new sparse merge table
    return make_sparse_st(id_gen)

#######
# Update and output
#######
def update_mt(t_now, t_new):
    """ Write to one merge matrix from another

    Arguments
    ----------
    t_now: lil_matrix
        The matrix to write
    t_new: lil_matrix
        The matrix to read 
    """
    all_roots = t_now.data[0]
    all_regions = t_now.data[1]

    # Merg each key into root and region
    for key, root, region in zip(t_new.rows[0], *t_new.data):
        # Get current root and region
        if root in t_now.rows[0]:
            root = t_now[0, root]
            region = t_now[1, root]
        # All key now merge to root and region
        for i in range(t_now.nnz // MERGE_DAT):
            if all_roots[i] == key:
                all_roots[i] = root
                all_regions[i] = region
        # Merge k to root and region
        t_now[0, key] = root
        t_now[1, key] = region

def update_st(t_now, t_new):
    """ Write to one split matrix from another

    Arguments
    ----------
    t_now: lil_matrix
        The matrix to write
    t_new: lil_matrix
        The matrix to read 
    """
    for split_dat in zip(t_new.rows[0], *t_new.data):
        key = split_dat[0]
        for i in range(SPLIT_DAT):
            t_now[i, key] = split_dat[i + 1]

def safe_makedirs(path):
    """ Make a directory if doesn't exist

    Arguments
    ----------
    path: str
    """
    try: 
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise

def save_mt(path, mt_now):
    """ Save the current merges to a file

    Arguments
    ----------
    path: str
    mt_now: lil_matrix
        Contains all current merges
    """
    merge_path = get_merge_file(path)
 
    all_merges = np.uint64([
        ## Only use rows with merge roots
        mt_now.rows[0],
        mt_now.data[0],
        mt_now.data[1],
    ]).T
    try: 
        path_error = safe_makedirs(path)
        np.save(merge_path, all_merges)
    except OSError as e:
        return str(e)
    return ''

def save_st(path, st_now):
    """ Save the current splits to a file

    Arguments
    ----------
    path: str
    st_now: lil_matrix
        Contains all current splits
    """
    split_path = get_split_file(path)
    all_splits = np.uint64([
        ## Only use rows with merge roots
        st_now.rows[0],
        st_now.data[0],
        st_now.data[1],
        st_now.data[2],
        st_now.data[3],
        st_now.data[4],
        st_now.data[5],
        st_now.data[6],
    ]).T
    try: 
        path_error = safe_makedirs(path)
        np.save(split_path, all_splits)
    except OSError as e:
        return str(e)
    return ''

def from_sparse_st(st_now):
    """ List parameters from a sparse split table 

    Arguments
    ----------
    st_now: lil_matrix
        All splits in 1D sparse array

    Returns
    --------
    [str]
        List of all split subregions
    """
    split_list = []

    def write_id(split_dat):
        dat = tuple(np.uint64(split_dat) - 1)
        # Swap the first two items
        out_dat = dat[1::-1]+dat[2:]
        # Separate with colons
        return ":".join(map(str, out_dat))

    for split_dat in zip(st_now.rows[0], *st_now.data):
        split_list.append(write_id(split_dat))

    return split_list

def from_sparse_mt(mt_now):
    """ Make disjoint sets from a sparse merge table 

    Arguments
    ----------
    mt_now: lil_matrix
        All merges in 1D sparse array

    Returns
    --------
    [[str]]
        List of all merged lists of ids
    """
    merge_dict = {}

    def write_id(key, region):
        if region > 1:
            return "{}:{}".format(key - 1, region - 1)
        return str(key - 1)

    # All entries in sparse array
    for key, root, region in zip(mt_now.rows[0], *mt_now.data):
        # Add to the merge list or an empty list
        v_list = merge_dict.get(root - 1, [])
        v_list.append(write_id(key, region))
        # Add new list to dictionary
        merge_dict[root - 1] = v_list

    # Return all lists of values
    return merge_dict.values()
