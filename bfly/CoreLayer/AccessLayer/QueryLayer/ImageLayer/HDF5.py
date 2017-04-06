from Datasource import Datasource
import numpy as np
import h5py
import json
import os

class HDF5(Datasource):
    """ Loads images from hdf5 files

    Attributes
    ------------
    _read: list
        All load functions for :data:`_meta_files`
    """

    # All readers for _meta_files
    _read = [json.load]
    #: All extensions of files pointing to h5
    _meta_files = ['.json']

    @staticmethod
    def load_tile(t_query):
        """load a single tile (image)

        Gets the image path from the \
:data:`TileQuery.RUNTIME`. ``IMAGE`` attribute.

        Gets the position of the image with the whole \
volume from :meth:`TileQuery.all_scales`, \
:meth:`TileQuery.tile_origin`, and \
:meth:`TileQuery.blocksize`.

        Arguments
        -----------
        t_query: :class:`TileQuery`
            With file path and image position

        Returns
        np.ndarray
            An image array that may be as large \
as an entire full resolution slice of \
the whole hdf5 volume. Based on the value \
of :meth:`TileQuery.all_scales`, this array \
will likely be downsampled by to a small fraction \
of the full tile resolution.
        """
        # call superclass
        Datasource.load_tile(t_query)
        # Load data for all the h5 files
        h5_files = t_query.RUNTIME.IMAGE.SOURCE.HDF5.VALUE
        # Get all the z indices and coordinates
        z_starts = enumerate(zip(*h5_files)[-1])

        # Find the region to crop
        sk,sj,si = t_query.all_scales
        z0,y0,x0 = t_query.tile_origin
        z1,y1,x1 = t_query.tile_origin + t_query.blocksize

        # get the right h5 file for the current z index
        all_z = (i for i, z in z_starts if z < z0)
        h5_file = h5_files[next(all_z, 0)]

        # Add the h5_file z offset
        z0 += h5_file[-1]
        z1 += h5_file[-1]

        # Load the image region from the h5 file
        with h5py.File(h5_file[0]) as fd:
            vol = fd[h5_file[1]]
            return vol[z0:z1:sk,y0:y1:sj,x0:x1:si]

    @staticmethod
    def preload_source(t_query):
        """load info from example tile (image)

        Calls :meth:`valid_path` to get filename and \
inner dataset path for the full h5 image volume.

        Then gets three needed values from the given \
path from the :class:`TileQuery` t_query

        Arguments
        -----------
        t_query: :class:`TileQuery`
            Only the file path is needed

        Returns
        --------
        dict
            Will be empty if :meth:`valid_path` finds\
this filname to not give a valid h5 volume.

            * :class:`RUNTIME` ``.IMAGE.BLOCK.NAME``
                (numpy.ndarray) -- 3x1 for any give tile shape
            * :class:`OUTPUT` ``.INFO.TYPE.NAME``
                (str) -- numpy dtype of any given tile
            * :class:`OUTPUT` ``.INFO.SIZE.NAME``
                (numpy.ndarray) -- 3x1 for full volume shape
        """
        # Keyword names
        output = t_query.OUTPUT.INFO
        runtime = t_query.RUNTIME.IMAGE
        k_h5 = runtime.SOURCE.HDF5.NAME
        # call superclass
        Datasource.preload_source(t_query)

        # Check if path is valid
        keywords = HDF5.valid_path(t_query)
        if not keywords:
            return {}

        # Validate first file name and dataset
        filename = keywords[k_h5][0][0]
        dataset = keywords[k_h5][0][1]
        # Load properties from H5 dataset
        with h5py.File(filename,'r') as fd:
            # Get the volume
            vol = fd[dataset]
            # Get a blockshape as a flat section
            block = [1, vol.shape[1], vol.shape[2]]
            # return named keywords
            keywords.update({
                output.TYPE.NAME: str(vol.dtype),
                runtime.BLOCK.NAME: np.uint32(block),
                output.SIZE.NAME: np.uint32(vol.shape)
            })
        # Return all canonical keywords
        return keywords

    @staticmethod
    def valid_path(t_query):
        """ Check if filename can access h5 data

        The filename can be a path to a json file \
that lists an h5 file and dataset path, or \
the filename can be a direct path to an h5 \
file. In either case the 'outer' file path \
directly to the h5 file and the 'inner' \
dataset path will be returned.

        Arguments
        -----------
        t_query: :class:`TileQuery`
            Only the file path is needed

        Returns
        --------
        dict
            Empty if not a valid h5 volume

            * :class:`RUNTIME` ``.IMAGE.SOURCE.HDF5.OUTER.NAME``
                (str) -- The direct filename to an hdf5 file
            * :class:`RUNTIME` ``.IMAGE.SOURCE.HDF5.INNER.NAME``
                (str) -- The datset in the file with image data
        """
        # Dereference path to hdf5 data
        k_h5 = t_query.RUNTIME.IMAGE.SOURCE.HDF5.NAME
        h5_list = HDF5.load_info(t_query)
        # load all the files
        for h5_file in h5_list:
            try:
                # Try to load one file
                with h5py.File(h5_file[0],'r') as fd:
                    if h5_file[1] not in fd.keys():
                        h5_file[1] = fd.keys()[0]
            except IOError:
                return {}

        # sort by z start
        def z_sort(h_file):
            return h_file[-1]

        # return reverse sorted files
        return {
            k_h5: sorted(h5_list, key=z_sort, reverse=True)
        }


    @staticmethod
    def get_details(h5_info, file_dict):
        """ Get all needed h5 file info from a pointer file

        Arguments
        ----------
        file_dict: dict
            Contains keys for INNER, OUTER, and OFF values

        Returns
        --------
        list
            All INNER, OUTER, OFF values in a flat list
        """

        # Get values for actual hdf5 file
        outer_path = file_dict.get(h5_info.OUTER.NAME)
        inner_path = file_dict.get(h5_info.INNER.NAME)
        z_offset = file_dict.get(h5_info.OFF.NAME, 0)

        return [outer_path, inner_path, z_offset]

    @staticmethod
    def load_info(t_query):
        """ Gets the h5 volume filename and datapath

        If the t_query path has an extension in \
the :data:`_meta_files` and the file contains \
``RUNTIME.IMAGE.SOURCE.HDF5.OUTER.NAME`` \
and ``RUNTIME.IMAGE.SOURCE.HDF5.INNER.NAME`` \
keys, then the values of those keys are returned. \
If any of those statements is not true, then the \
original t_query path is returned along with the \
default dataset given by \
``RUNTIME.IMAGE.SOURCE.HDF5.INNER.VALUE``.

        Arguments
        -----------
        t_query: :class:`TileQuery`
            Only the file path is needed

        Returns
        --------
        list
            * The direct filename to an hdf5 file
            * The datset in the file with image data
        """
        # Load information about full hdf5
        h5_info = t_query.RUNTIME.IMAGE.SOURCE.HDF5
        filename = t_query.OUTPUT.INFO.PATH.VALUE
        dataset = h5_info.INNER.VALUE

        # Get all details for info
        def get_details(info):
            return HDF5.get_details(h5_info, info)

        # Load path if ends with json
        ending = os.path.splitext(filename)[1]
        if ending in HDF5._meta_files:
            # Get function to read the metainfo file
            order = HDF5._meta_files.index(ending)
            try:
                with open(filename) as infile:
                    # Read the metainfo file
                    info = HDF5._read[order](infile)
            except IOError:
                return [[filename, dataset, 0]]
            ######
            ## Handle references to multiple h5 files
            ## Get first item in list
            ######
            if isinstance(info, list):
                return map(get_details, info)
            # Get the inner dataset and the new path
            return [get_details(info)]

        return [[filename, dataset, 0]]

