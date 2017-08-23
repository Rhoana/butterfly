import numpy.random as npr
import numpy as np
import h5py
import json
import os

def full_path(path):
    """ Prepend this file's directory to the path
    """
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, path)

def write_synapses(k_files, data_path, synapse_pairs, synapse_centers):
    """ write to synapse-connections.json

    Arguments
    ------------
        k_files: NamedStruct
            The constants for a synapse file
        data_path: str
            The path to the output folder
        synapse_pairs: np.ndarray
            An Nx2 array of pairs for synapses
        synapse_centers: np.ndarray
            An Nx3 array of synapse locations

    Returns
    ---------
        dict
            The data as written
    """
    # Get constant keywords
    k_neurons = k_files.SYNAPSE.NEURON_LIST
    k_center = k_files.SYNAPSE.POINT.NAME
    k_shape = k_files.SYNAPSE.POINT.LIST
    # Format neuron pairs and coordinates
    synapse_dict = dict(zip(k_neurons, synapse_pairs.T.tolist()))
    synapse_dict.update({
        k_center: dict(zip(k_shape, synapse_centers.T.tolist()))
    })

    # Make a data directory
    if not os.path.exists(data_path):
        os.makedirs(data_path)
    # Write the data to file
    k_out = k_files.SYNAPSE.DEFAULT
    with open(os.path.join(data_path, k_out), 'w') as sf:
        json.dump(synapse_dict, sf)

    # Return the written data
    return synapse_dict

def write_neurons(k_files, data_path, neuron_ids, neuron_centers):
    """ write to neuron-soma.json

    Arguments
    ------------
        k_files: NamedStruct
            The constants for a soma file
        data_path: str
            The path to the output folder
        neuron_ids: np.ndarray
            A flat array of all neuron ids
        neuron_centers: np.ndarray
            An Nx3 array of soma locations

    Returns
    ---------
        dict
            The data as written
    """
    soma_list = []
    k_soma = ['neuron_id', 'z', 'y', 'x']
    # Format neuron labels and coordinates
    for nrn, zyx in zip(neuron_ids, neuron_centers):
        full_soma = np.r_[nrn, zyx].tolist()
        # Add labels and coordinates to a dictionary
        soma_dict = dict(zip(k_soma, full_soma))
        soma_list.append(soma_dict)

    # Make a data directory
    if not os.path.exists(data_path):
        os.makedirs(data_path)
    # Write the data to file
    k_out = k_files.SOMA.DEFAULT
    with open(os.path.join(data_path, k_out), 'w') as sf:
        json.dump(soma_list, sf)

    # Return the written data
    return soma_list

def make_neurons(neuron_n, info, seed):
    """ Make a number of neurons of a given data type

    Arguments
    ----------
    neuron_n: int
        The number of neurons to make
    info: np.iinfo
        Contains the dtype max and value
    seed: int
        The seed for predictable noise

    Returns
    --------
    np.ndarray:
        All the neurons
    np.ndarray:
        All the other ids
    """

    npr.seed(seed)
    # Choice within max without replacement
    ids = npr.choice(info.max, 2*neuron_n, True)
    ids = ids.astype(info.dtype)
    # Return all neurons and all others
    neurons, others = np.split(ids, 2)
    # Make sure 0 is not a neuron
    if 0 in neurons:
        return others, neurons
    # Return normally
    return neurons, others

def make_synapses(synapse_n, neuron_ids, info, seed):
    """ Make neuron pairs of a given data type

    Arguments
    ----------
    synapse_n: int
        The number of neuron pairs to make
    neuron_ids: np.ndarray
        All the neurosn to choose from
    info: np.iinfo
        Contains the dtype max and value
    seed: int
        The seed for predictable noise

    Returns
    --------
    np.ndarray:
        Nx2 array of all pairs
    """

    pairs = np.zeros([2, synapse_n], dtype=info.dtype)
    # Both pairs
    for i in range(2):
        npr.seed(seed + i)
        pairs[i] = npr.choice(neuron_ids, synapse_n)
    return pairs.T

def make_centers(n_centers, zyx_shape, info, seed):
    """ Make many 3D vectors of a given data type

    Arguments
    ----------
    n_centers: int
        The number of centers to make
    zyx_shape: list
        The 3 dimensions of the volume
    info: np.iinfo
        Contains the dtype max and value
    seed: int
        The seed for predictable noise

    Returns
    --------
    np.ndarray:
        Nx3 array of all vectors
    """

    zyx = np.zeros([3, n_centers], dtype=info.dtype)
    # All three dimensions
    for i in range(3):
        npr.seed(seed + i)
        zyx[i] = npr.choice(zyx_shape[i], n_centers)
    return zyx.T

def write_h5(channel_path, volume):
    """ write a dummy volume to an h5 file

    Arguments
    ----------
    channel_path: str
        The path to save the h5 file
    zyx_shape: list
        The 3 dimensions of the volume
    info: np.iinfo
        Contains the dtype max and value
    """
    # Create the file from a path
    with h5py.File(channel_path, 'w') as fd:
        fd.create_dataset('stack', data = volume)

def make_volume(zyx_shape, info, seed):
    """ make a dummy volume for testing

    Arguments
    ----------
    zyx_shape: list
        The 3 dimensions of the volume
    info: np.iinfo
        Contains the dtype max and value
    seed: int
        The seed for predictable noise

    Returns
    --------
    np.ndarray
        A 3D Volume of random integers
    """
    # Make a random array
    npr.seed(seed)
    return npr.randint(0, info.max, zyx_shape, info.dtype)
