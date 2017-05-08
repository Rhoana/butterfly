from Datasource import Datasource
import numpy as np
import h5py
import json
import os

class TiffGrid(Datasource):
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
        --------
        None
        """
        # call superclass
        Datasource.load_tile(t_query)

        return None

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
        return {}
        # Keyword names
        output = t_query.OUTPUT.INFO
        runtime = t_query.RUNTIME.IMAGE
        k_h5 = runtime.SOURCE.HDF5.NAME
        # Get the max block size in bytes for a single tile
        max_bytes = t_query.RUNTIME.CACHE.MAX_BLOCK.VALUE

        # call superclass
        Datasource.preload_source(t_query)

        # Validate highest in z file name and dataset
        filename = keywords[k_h5][-1][0]
        dataset = keywords[k_h5][-1][1]
        offset = keywords[k_h5][-1][2]
        # Load properties from H5 dataset
        with h5py.File(filename,'r') as fd:
            # Get the volume
            vol = fd[dataset]
            # Get a shape for all the files
            shape = np.uint32(vol.shape)
            shape[0] += offset
            ####
            # Get a blockshape as a flat section
            ####
            # Get the bytes for a full slice
            voxel_bytes = np.uint32(vol.dtype.itemsize)
            slice_bytes = voxel_bytes * np.prod(shape[1:])
            # Get the nearest tile size under cache limit
            square_overage = np.ceil(slice_bytes / max_bytes)
            side_scalar = np.ceil(np.sqrt(square_overage))
            # Set the actual blocksize to be under the cache limit
            plane_shape = np.ceil(shape[1:] / side_scalar)
            max_block = np.r_[[1], plane_shape]
            ####
            # Get max blocksizes for different resolutions
            ####
            lo_res = 10
            # Get all block sizes by halving the max block size
            all_blocks = [shape/(2**res) for res in range(lo_res)]
            block_array = np.clip(np.ceil(all_blocks), 1, max_block)
            # return named keywords
            keywords.update({
                runtime.BLOCK.NAME: np.uint32(block_array),
                output.SIZE.NAME: np.uint32(shape),
                output.TYPE.NAME: str(vol.dtype),
            })
        # Return all canonical keywords
        return keywords


