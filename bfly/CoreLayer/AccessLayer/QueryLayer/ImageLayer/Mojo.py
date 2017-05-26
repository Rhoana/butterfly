from Datasource import Datasource
import xml.etree.ElementTree as ET
import tifffile as tiff
import numpy as np
import h5py
import cv2
import os

class Mojo(Datasource):
    """ Interface to mojo tiled image folder structure
    """
    _meta = 'tiledVolumeDescription.xml'

    @classmethod
    def load_tile(cls, t_query):
        """load a single tile (image)

        Arguments
        -----------
        t_query: :class:`TileQuery`
            With file path and image position

        Returns
        -----------
        np.ndarray
            An image array that may be as large \
as an entire full resolution slice of \
the whole hdf5 volume. Based on the value \
of :meth:`TileQuery.all_scales`, this array \
will likely be downsampled by to a small fraction \
of the full tile resolution.
        """
        # Get the offset for the tile
        i_z, i_y, i_x = t_query.index_zyx
        # Get the format for the tile
        source_field = t_query.RUNTIME.IMAGE.SOURCE
        format_field = source_field.MOJO.FORMAT
        fmt = format_field.VALUE
        # Get the raw input resolution
        res_xy = t_query.INPUT.RESOLUTION.XY.VALUE

        # Format the file path
        base_path = os.path.join(t_query.path, 'tiles')
        # Get the w and z subfolders 
        w_folder = 'w={:08d}'.format(res_xy)
        z_folder = 'z={:08d}'.format(i_z)
        # Get the file name with y, x and file extension
        f_name = 'y={:08d},x={:08d}.{}'.format(i_y,i_x,fmt)

        # Get the full file path
        full_path = os.path.join(base_path, w_folder, z_folder, f_name)
        # Make an output array from the scaled blocksize
        dtype = getattr(np, t_query.OUTPUT.INFO.TYPE.VALUE)
        vol = np.zeros(t_query.blocksize, dtype = dtype)

        # If the path does not exist
        if not os.path.exists(full_path):
            return vol

        # If the type is hdf5
        if fmt in format_field.H5_LIST:
            with h5py.File(full_path) as fd:
                # Read the first dataset
                vol = fd[fd.keys()[0]][:]
        else:
            # Read the image with cv2 or tiff
            vol = cls.imread(full_path)[:]

        # Make sure 3d array
        if len(vol.shape) == 2:
            return vol[np.newaxis]
        return vol

    @classmethod
    def preload_source(cls, t_query):
        """load info from example tile (image)

        Arguments
        -----------
        t_query: :class:`TileQuery`
            Only the file path is needed

        Returns
        --------
        dict
            Will be empty if filename does not give \
a valid mojo directory.

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
        k_format = runtime.SOURCE.MOJO.FORMAT.NAME

        # Get the name and ending of the target folder
        path_name = t_query.OUTPUT.INFO.PATH.VALUE
        meta_file = os.path.join(path_name, cls._meta)

        # Return if no meta file for mojo
        if not os.path.exists(meta_file):
            return {}

        # Load the meta info
        meta_info = ET.parse(meta_file).getroot().attrib

        # Estimate the data type
        n_bytes = int(meta_info['numBytesPerVoxel'])
        dtype = 'uint{}'.format(8 * n_bytes)
        # Get the data file exension
        file_ext = meta_info['fileExtension']
        # Get the block shape and full size
        block_z = meta_info['numVoxelsPerTileZ']
        block_y = meta_info['numVoxelsPerTileY']
        block_x = meta_info['numVoxelsPerTileX']
        full_z = meta_info['numVoxelsZ']
        full_y = meta_info['numVoxelsY']
        full_x = meta_info['numVoxelsX']

        return {
            runtime.BLOCK.NAME: np.uint32([[block_z, block_y, block_x]]),
            output.SIZE.NAME: np.uint32([full_z, full_y, full_x]),
            output.TYPE.NAME: dtype,
            k_format: file_ext,
        }

    @staticmethod
    def imread(_path):
        """ allow loading jpg, png as well as tif
        """
        if os.path.splitext(_path)[1] in ['.tiff', '.tif']:
            return tiff.imread(_path)
        else:
            return cv2.imread(_path,0)

