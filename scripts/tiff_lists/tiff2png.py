import os
import cv2
import json
import argparse
import numpy as np
from tiffMGMT import TiffMGMT

if __name__ == '__main__':

    help = {
        'tiff2set': 'Get all values in a region a list of tiff files',
        'files': 'The path to a json file listing all tiff files',
        'out': 'The folder to save all the png files (./out)',
    }
    # Read the arguments correctly
    parser = argparse.ArgumentParser(description=help['tiff2set'])
    # Define all the arguments
    parser.add_argument('files', help=help['files'])
    parser.add_argument('--out', '-o', default='out', help=help['out'])
    # Read the argumentss into a dictionary
    argd = vars(parser.parse_args())
    # Format the path arguments properly
    def fmt_path(k):
        return os.path.abspath(os.path.expanduser(argd[k]))
    in_file, out_folder = map(fmt_path, ['files', 'out'])
    # Create a file manager
    mgmt = TiffMGMT(in_file)

