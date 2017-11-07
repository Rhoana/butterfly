from scipy.sparse import lil_matrix
import numpy as np
import scipy
import sys
import os

TYPES = [
    scipy.sparse.lil.lil_matrix,
]
NPZ_EXT = ".edit.npz"

def name_npz(path):
    """ Concat NPZ_EXT to a filenmae
    
    Arguments
    ----------
    path: str
        The path to a whole datasource volume

    Returns
    --------
    str
       The filename for all edits  

    """
    return path.rstrip(os.sep)+NPZ_EXT
    
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
def sparse_1d(data, rows):
    """ Make a 1D sparse vector of max length

    Arguments
    ----------
    data : np.ndarray
        values for each row given
    rows : np.ndarray
        all rows with a given value

    Returns
    --------
    lil_matrix
        Vector of all 64-bit unsigned ints
    """
    T_SHAPE = (1, sys.maxsize)
    out_vec = lil_matrix(T_SHAPE, dtype=np.int64)
    for r,d in zip(rows, data):
        out_vec[0, r] = d
    return out_vec

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
    npz_path = name_npz(path)
    if not os.path.exists(npz_path):
        merges = sparse_1d([],[])
        return (merges,)
    with np.load(npz_path) as d:
        merges = sparse_1d(d['merge'], d['rows'])
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
    data = [int(m[0]) + 1 for m in sv_new for _ in m]
    rows = [int(i) + 1 for m in sv_new for i in m]
    # Make new sparse merge table
    return sparse_1d(data, rows)

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
    # Write each new value to current key
    for k,v in zip(t_new.rows[0], t_new.data[0]):
        # Get current value for v
        if (v in t_now.rows[0]):
            v = t_now[0,v]
        # All merged to k now merge to v
        for i in range(t_now.nnz):
            if all_roots[i] == k:
                all_roots[i] = v
        # Merge k to v
        t_now[0,k] = v

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
    npz_path = name_npz(path)
    keywords = {
        'merge': mt_now.data[0],
        'rows': mt_now.rows[0],
    }
    try: 
        path_error = safe_makedirs(path)
        np.savez(npz_path, **keywords)
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
    # All entries in sparse array
    for k,v in zip(mt_now.rows[0], mt_now.data[0]):
        # Add to the merge list or an empty list
        v_list = merge_dict.get(v - 1, [])
        v_list.append(str(k - 1))
        # Add new list to dictionary
        merge_dict[v - 1] = v_list

    # Return all lists of values
    return merge_dict.values()
