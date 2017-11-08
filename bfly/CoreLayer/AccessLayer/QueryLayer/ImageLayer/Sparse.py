import logging as log
from scipy.sparse import lil_matrix
import numpy as np
import scipy
import sys
import os

TYPES = [
    scipy.sparse.lil.lil_matrix,
]
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
       The filename for all edits  

    """
    return path.rstrip(os.sep)+MERGE_EXT
    
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
def sparse_merge(id_gen):
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
    for key, root, region in id_gen:
        t_merge[0, key] = root
        t_merge[1, key] = region
    return t_merge

def load(path):
    """ Read all sparse matrices in edits file

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
        merges = sparse_merge(iter(()))
        return (merges,)
    saved_merges = np.load(merge_path, mmap_mode='r')
    merges = sparse_merge(iter(saved_merges))
    return (merges,)

def to_sparse(sv_new):
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
    return sparse_merge(id_gen)

#######
# Update and output
#######
def update(t_now, t_new):
    """ Write to one sparse matrix from another

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
        if (root in t_now.rows[0]):
            root = t_now[0, root]
            region = t_now[1, root]
        # All key now merge to root and region
        for i in range(t_now.nnz / MERGE_DAT):
            if all_roots[i] == key:
                all_roots[i] = root
                all_regions[i] = region
        # Merge k to root and region
        t_now[0, key] = root
        t_now[1, key] = region

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

def save(path, mt_now):
    """ Save the current edits to a file

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

def from_sparse(mt_now):
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
