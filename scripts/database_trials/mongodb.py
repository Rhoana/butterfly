import os
import json
import numpy as np
from pymongo import MongoClient
from pymongo import ASCENDING

class MongoDB():
    def __init__(self, port):
        # Connect to the mongo client
        self.client = MongoClient('localhost', port)
        # Create or open the experiment database
        self.database = self.client['experiment']
        # Create or open the synapse_keypoints collection
        self.collection = self.database['synapse_keypoints']

    def add_points(self, entries):
        # Map all the entries to a dictionary
        pairs = enumerate(entries)
        dicts = [dict(zyx=v.tolist(), id=i) for i,v in pairs]
        # Create the synapse index
        id_index = [('id', ASCENDING)]
        self.collection.create_index(id_index, unique=True)
        # Add all the dictionaries to the collection
        all_keys = self.collection.insert_many(dicts)

    def check_key(self, key):
        # Return the list for the given key
        found = self.collection.find_one({'id': key})
        return found.get('zyx') if found else []

    def reset(self):
        # Clear the collection
        self.collection.remove()
