from Query import Query
from ImageLayer import Sparse
import numpy as np
import json, yaml

VOXEL_XYZ = np.uint32([4,4,30])

class NumpyEncoder(json.JSONEncoder):
    """ Encode numpy datatypes in json
    """
    def default(self, obj):
        """ Serialize numpy numbers as usual
        """
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NumpyEncoder, self).default(obj)

class InfoQuery(Query):
    """ Describe ``INPUT.METHODS.INFO_LIST`` requests

    Arguments
    -----------
    args: list
        unused
    keywords: dict
        * `OUTPUT.INFO.NAMES` (list) --
            all answers to group and feature queries
        * `OUTPUT.INFO.PATH` (str) --
            the path to the given :class:`Datasource`
        * `OUTPUT.INFO.SIZE` (numpy.ndarray) --
            3x1 for full volume shape
        * `OUTPUT.INFO.CHANNEL` (str) --
            The name of the most specific image group
        * `OUTPUT.INFO.FORMAT` (str) --
            The requested format for HTTP output

    Attributes
    ------------
    _write: list
        All write functions for output formats
    """

    #: Options for all :data:`_write`
    _form = [
        {
            'indent': 4,
            'cls': NumpyEncoder
        },
        {
            'default_flow_style': False
        }
    ]
    # All writers for output formats
    _write = [json.dumps, yaml.dump]

    def update_keys(self, keywords):

        Query.update_keys(self, keywords)

        for key in ['NAMES','PATH','SIZE','CHANNEL']:
            self.set_key(self.OUTPUT.INFO,key)

        self.set_key(self.INPUT.INFO,'FORMAT')

        # For the dataset queries
        self.set_key(self.OUTPUT.INFO, 'CHANNELS')
        self.set_key(self.OUTPUT.INFO, 'DATASET')

    @property
    def channels(self):
        """ return the list of channels

        Returns
        -------
        list
            All channel dictionaries
        """
        return self.OUTPUT.INFO.CHANNELS.VALUE

    @property
    def get_format(self):
        """ get the index of the output format

        Returns
        -------
        int
            index for :data:`_form` or :data:`_write`
        """
        fmt_val = self.INPUT.INFO.FORMAT.VALUE
        return self.INPUT.INFO.FORMAT.LIST.index(fmt_val)

    def websocket_edit(self, msg={}):
        """ Change internal state based on websocket message

        Arguments
        -------------
        msg: dict
            The commands controlling the message

        Returns
        --------
        dict
            The values changed in the internal state
        """
        methods = self.INPUT.METHODS
        action = methods.VALUE.split(':')[1]
        # take named keywords
        merge_field = self.RUNTIME.IMAGE.MERGE
        split_field = self.RUNTIME.IMAGE.SPLIT
        error_field = self.RUNTIME.IMAGE.ERROR
        # Save merges in message
        if action in ['save']:
            # Get the new merges
            merge_new = msg.get('merge', [])
            mt_new = Sparse.to_sparse_mt(merge_new)
            # Get the new splits
            split_new = msg.get('split', [])
            st_new = Sparse.to_sparse_st(split_new)
            # Update the current merges
            mt_now = merge_field.VALUE
            Sparse.update_mt(mt_now, mt_new)
            # Update the current splits
            st_now = split_field.VALUE
            Sparse.update_st(st_now, st_new)
            # Write and return current merges and splits
            e_path = self.edit_path
            error0 = Sparse.save_mt(e_path, mt_now)
            error1 = Sparse.save_st(e_path, st_now)
            # Update Error message
            return {
                merge_field.NAME: mt_now,
                split_field.NAME: st_now,
                error_field.NAME: error0 + error1,
            }
        # Unchanged
        return {}

    def websocket_result(self, action):
        """ Results to a websocket query
        
        Arguments
        ----------
        action: str
            The type of result to send to client

        Returns
        --------
        dict
            The result to send to client
        """
        # take named keywords
        merge_field = self.RUNTIME.IMAGE.MERGE
        split_field = self.RUNTIME.IMAGE.SPLIT
        error_field = self.RUNTIME.IMAGE.ERROR
        # Standard results
        result = {
            'action': action,
            'error': error_field.VALUE,
        }
        # Restore and save return the same
        if action in ['save', 'restore']:
            # Format the merge and split tables as output
            mt_now = merge_field.VALUE
            st_now = split_field.VALUE
            return dict({
                'merge': Sparse.from_sparse_mt(mt_now),
                'split': Sparse.from_sparse_st(st_now),
            }, **result)

        return result

    @property
    def result(self):
        """ get the answer to the info query

        Returns
        -------
        dict
            For the method ``INPUT.METHODS.META.NAME``:

            * ``OUTPUT.INFO.PATH.NAME`` --
                (str) ``OUTPUT.INFO.PATH.VALUE``
            * ``OUTPUT.INFO.TYPE.NAME`` --
                (str) ``OUTPUT.INFO.TYPE.VALUE``
            * ``OUTPUT.INFO.SIZE.NAME`` --
                (dict) ``OUTPUT.INFO.SIZE.VALUE``
            * ``OUTPUT.INFO.CHANNEL.NAME`` --
                (str) ``OUTPUT.INFO.CHANNEL.VALUE``
        list
            For all methods ``INPUT.METHODS.GROUP_LIST``:
            For the method ``INPUT.METHODS.FEATURE.NAME``:

            * all (str) in ``OUTPUT.INFO.NAMES.VALUE``
        """

        info_out = self.OUTPUT.INFO
        methods = self.INPUT.METHODS
        source_field = self.RUNTIME.IMAGE.SOURCE
        # Return a list of all group naems
        if methods.VALUE in methods.GROUP_LIST:
            return info_out.NAMES.VALUE
        # Return fake "precomputed" file
        if methods.VALUE == methods.PRE.NAME:
            # Check if image or segmentation
            dtype = info_out.TYPE.VALUE
            is_id = dtype in info_out.TYPE.ID_LIST
            # Get the blocksizes
            block_zyx = self.RUNTIME.IMAGE.BLOCK.VALUE
            block_xyz = np.fliplr(block_zyx)
            # All block info
            resolutions = range(len(block_xyz))
            block_enum = zip(resolutions, block_xyz)
            # Constant info
            full_size = [
                info_out.SIZE.VALUE['x'],
                info_out.SIZE.VALUE['y'],
                info_out.SIZE.VALUE['z'],
            ]
            
            # Format all scales
            def get_scale(rb):
                r,b = rb
                return {
                    'key': str(r),
                    'size': full_size,
                    'resolution': [2**r, 2**r, 1]*VOXEL_XYZ,
                    'voxel_offset': [0,0,0],
                    'chunk_sizes': [list(b)],
                    'encoding': 'raw',
                }

            all_info = {
                'num_channels': 1,
                'data_type': dtype,
                'scales': list(map(get_scale, block_enum)),
                'type': ['image', 'segmentation'][is_id],
                'mesh': 'mesh',
            }

            return all_info
        # Return dictionary created here
        if methods.VALUE == methods.META.NAME:
            return {
                source_field.NAME: source_field.VALUE,
                info_out.PATH.NAME: info_out.PATH.VALUE,
                info_out.TYPE.NAME: info_out.TYPE.VALUE,
                info_out.SIZE.NAME: info_out.SIZE.VALUE,
                info_out.CHANNEL.NAME: info_out.CHANNEL.VALUE,
            }
        # Handle websocket events
        if self.is_websocket:
            ws_actions = methods.VALUE.split(':')[1:]
            return self.websocket_result(*ws_actions)
        # Return list of groups
        return info_out.NAMES.VALUE

    @property
    def dump(self):
        """ format :meth:`result` with :data:`write`

        Returns
        --------
        str
            The :meth:`result` formatted as a string
        """
        raw_output = self.result
        # Write as JSON or YAML
        out = self.get_format
        writer = self._write[out]
        return writer(raw_output,**self._form[out])

    def dump_dataset(self, all_channels):
        """ format :meth:`result` with :data:`write`
        
        Arguments
        ----------
        all_channels: list
            Contains keywords for each channel

        Returns
        --------
        str
            The :meth:`result` formatted as a string
        """

        # Get keys for interface
        name_key = self.OUTPUT.INFO.CHANNEL.NAME
        type_key = self.OUTPUT.INFO.TYPE.NAME
        # Get interface constants
        annotation_list = self.OUTPUT.INFO.TYPE.ID_LIST
        # Get interface values
        dataset = self.OUTPUT.INFO.DATASET.VALUE
 
        # Format channel for this output
        def fmt_channel(chans, ch):
            # Get data type and channel type
            channel_type = 'image'
            data_type = ch[type_key]
            if data_type in annotation_list:
                channel_type = 'annotation'
            # Update channels dictionary
            chans.update({
                ch[name_key]: {
                    'datatype': data_type,
                    'channel_type': channel_type,
                    'description': ch[name_key],
                    "exceptions": 0,
                    "propagate": 2,
                    "readonly": 1,
                    "resolution": 0,
                    "windowrange": [
                        0,
                        0
                    ]
                }
            })
            return chans

        # Get keys for interface
        block_key = self.RUNTIME.IMAGE.BLOCK.NAME
        size_key = self.OUTPUT.INFO.SIZE.NAME

        # Get example channel
        channel0 = all_channels[0]
        # Get the number of scled levels
        block_list = channel0[block_key]
        n_levels = len(block_list)
        level_ids = range(n_levels)

        # Get constants
        k_offset = [0,0,0]
        k_fullsize = channel0[size_key]

        # Get scale for resolution
        def xyz_scale(i):
            return [2**i, 2**i, 1]
        xyz_scales = np.uint64(map(xyz_scale, level_ids))

        # Get voxel, block, and full sizes
        xyz_blocklist = np.fliplr(block_list)
        xyz_voxelres = np.uint64(VOXEL_XYZ * xyz_scales)
        xyz_fullsize =  np.uint64(k_fullsize[::-1] / xyz_scales)
        xyz_fullsize = np.clip(xyz_fullsize, 1, None)

        # Make a dictionary for all levels
        def level_dict(values):
            return dict(zip(level_ids, values))

        # Get all info for dataset
        raw_output = {
            'channels': reduce(fmt_channel, all_channels, {}),
            'dataset': {
                'scaling': 'zslices',
                'description': dataset,
                'scalinglevels': n_levels,
                'resolutions': level_ids,
                'offset': level_dict((k_offset,)*n_levels),
                'neariso_scaledown': level_dict((1,)*n_levels),
                'cube_dimension': level_dict(xyz_blocklist),
                'imagesize': level_dict(xyz_fullsize),
                'voxelres': level_dict(xyz_voxelres),
                'neariso_voxelres': level_dict(xyz_voxelres),
                'timerange': [
                    0,
                    0
                ],
            },
            'metadata': {},
            'project': {
                'description': dataset,
                'name': dataset,
                'version': '0.0'
            },
        }
        # Undocumented in NDStore v0.7
        def dataset_shim(d):
            d['neariso_offset'] = d['offset']
            d['neariso_voxelres'] = d['voxelres']
            d['neariso_imagesize'] = d['imagesize']
        
        dataset_shim(raw_output['dataset'])

        # Write as JSON or YAML
        out = self.get_format
        writer = self._write[out]
        return writer(raw_output,**self._form[out])

    def set_channel(self, channel):
        """ Change the query to a given channel
        
        channel: dict
            ``self.OUTPUT.INFO.CHANNEL``: str
            ``self.OUTPUT.INFO.PATH``: str
        """
        self.update_keys(channel)
        for key in ['PATH','CHANNEL']:
            self.set_key(self.OUTPUT.INFO,key)
