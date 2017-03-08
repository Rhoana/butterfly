from Webserver import Webserver
from toArgv import toArgv
from Settings import *
import DatabaseLayer
import sys, argparse
import logging
import json
import os

class Butterfly():
    '''
    Butterfly 2.0
    EM Data server
    2017 VCG + Lichtman Lab
    '''
    log_info = {
        'filename': 'bfly.log',
        'level': logging.INFO
    }
    def __init__(self,_argv):

        # keyword arguments
        self.INPUT = INPUT()
        self.RUNTIME = RUNTIME()
        self.OUTPUT = OUTPUT()

        # Get the port
        args = self.parseArgv(_argv)
        port = args['port']

        # Start to write to log files
        logging.basicConfig(**self.log_info)

        # Populate the database
        db = self.updateDB()

        # Start a webserver on given port
        Webserver(db).start(port)

    # Update the database from the config file
    def updateDB(self):
        # Create or open the database
        db_class = getattr(DatabaseLayer,DB_TYPE)
        self._db = db_class(DB_PATH)
        # Get keywords for the BFLY_CONFIG
        k_list = self.INPUT.METHODS.GROUP_LIST
        k_path = self.OUTPUT.INFO.PATH.NAME
        '''
        Make a dictionary mapping channel paths to dataset paths
        '''
        pather = lambda l: l.get(k_path,'')
        lister = lambda l,n: l.get(k_list[n],[])
        mapper  = lambda l,p: {c:p for c in map(pather,l)}
        join = lambda l,p,a: dict(mapper(l,p),**a) if p else a
        get_L2 = lambda a,l: join(lister(l,3), pather(l), a)
        get_L1 = lambda a,l: reduce(get_L2, lister(l,2), a)
        get_L0 = lambda a,l: reduce(get_L1, lister(l,1), a)
        all_paths = reduce(get_L0, lister(BFLY_CONFIG,0), {})

        # Fill the database with content
        return self.completeDB(all_paths)

    # Add all colections and content to the database
    def completeDB(self, all_paths):
        # Add paths to database
        self._db.add_paths(all_paths)
        # Get all dataset paths from all channel paths
        dataset_paths = set(all_paths.values())
        # Add all needed tables to the database
        self._db.add_tables(dataset_paths)
        # Add synapses and neurons to database
        map(self.addSynapseDB, dataset_paths)

        # Complete database
        return self._db

    def addSynapseDB(self,dataset_path):
        # Get keywords for the database
        k_file = self.RUNTIME.DB.FILE.SYNAPSE.NAME
        k_nodes = self.RUNTIME.DB.FILE.SYNAPSE.NEURON_LIST
        k_points = self.RUNTIME.DB.FILE.SYNAPSE.POINT.LIST
        k_point = self.RUNTIME.DB.FILE.SYNAPSE.POINT.NAME
        k_synapse = self.RUNTIME.DB.TABLE.SYNAPSE.NAME
        # Get the full path to the synapse file
        full_path = os.path.join(dataset_path, k_file)
        # List all the syapse database keys
        k_keys = k_nodes+k_points
        # For output file
        synapes_dicts = []

        # Begin adding synapses to database
        with open(full_path, 'r') as f:
            all_json = json.load(f)
            # Get points and centers from json
            get_node = lambda n: all_json[n]
            get_point = lambda p: all_json[k_point][p]
            # Transpose the list of all synapses
            center = map(get_point, k_points)
            link0, link1 = map(get_node, k_nodes)
            synapse_list = zip(link0,link1, *center)
            # Get a list of dictionaries for all synapses
            get_dict = lambda s: dict(zip(k_keys,s))
            synapse_dicts = map(get_dict, synapse_list)

        # Add the synapses to the database
        entry_args = [k_synapse,dataset_path,synapse_dicts]
        self._db.add_entries(*entry_args)
        # Add neurons to the database
        self.addNeuronDB(dataset_path,synapse_dicts)

    def addNeuronDB(self,dataset_path,synapse_dicts):
        # Get keywords for the database
        k_id = self.RUNTIME.DB.FILE.NEURON.ID.NAME
        k_nodes = self.RUNTIME.DB.FILE.SYNAPSE.NEURON_LIST
        k_points = self.RUNTIME.DB.FILE.NEURON.POINT.LIST
        k_neuron = self.RUNTIME.DB.TABLE.NEURON.NAME
        # Get constant for id and first/second neurons
        k_id = self.RUNTIME.DB.TABLE.NEURON.NAME

        # Get neuron from synapse
        get_n = [
            lambda d: d[k_nodes[0]],
            lambda d: d[k_nodes[1]]
        ]
        # Get id and center point for a neuron
        get_id = lambda d,n: {k_id: get_n[n](d)}
        get_point = lambda d: {k: d[k] for k in k_points}

        # Find targets that are never sources
        all_n1 = map(get_n[0], synapse_dicts)
        only_n2 = lambda s: get_n[1](s) not in all_n1
        only_n2_dicts = filter(only_n2, synapse_dicts)

        # Make dictionaries first from source neurons
        get_n1 = lambda d: dict(get_point(d), **get_id(d,0))
        n1_dicts = map(get_n1, synapse_dicts)
        # Add remaining dictionaires from target neurons
        get_n2 = lambda d: dict(get_point(d), **get_id(d,1))
        n2_dicts = map(get_n2, only_n2_dicts)
        # Get all the neuron dicts from synapses
        all_dicts = n1_dicts + n2_dicts

        # Add the neurons to the database
        entry_args = [k_neuron,dataset_path,all_dicts]
        self._db.add_entries(*entry_args)

    def parseArgv(self, argv):
        sys.argv = argv

        help = {
            'bfly': 'Host a butterfly server!',
            'folder': 'relative, absolute, or user path/of/all/experiments',
            'save': 'path of output yaml file indexing experiments',
            'port': 'port >1024 for hosting this server'
        }

        parser = argparse.ArgumentParser(description=help['bfly'])
        parser.add_argument('port', type=int, nargs='?', default=PORT, help=help['port'])
        parser.add_argument('-e','--exp', metavar='exp', help= help['folder'])
        parser.add_argument('-o','--out', metavar='out', help= help['save'])
        return vars(parser.parse_args())

def main(*_args, **_flags):
    return Butterfly(toArgv(*_args, **_flags))

if __name__ == "__main__":
    Butterfly(sys.argv)
