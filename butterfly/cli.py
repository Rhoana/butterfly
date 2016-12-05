import re
import os
import cv2
import yaml
import logging
import argparse
import numpy as np

def main():
    '''
    Butterfly
    EM Data server
    Eagon Meng and Daniel Haehn
    Lichtman Lab, 2015
    '''
    help = {
        'bfly': 'Host a butterfly server!',
        'folder': 'relative, absolute, or user path/of/all/experiments',
        'port': 'port >1024 for hosting this server',
        'depth': 'search nth nested subfolders of exp path (default 2)'
    }

    parser = argparse.ArgumentParser(description=help['bfly'])
    parser.add_argument('port', type=int, nargs='?', help=help['port'])
    parser.add_argument('-e','--exp', metavar='exp', help= help['folder'])
    parser.add_argument('-n','--nth',type=int, metavar='nth', default = 2, help= help['depth'])
    [homefolder,port,nth] = [parser.parse_args().exp, parser.parse_args().port, parser.parse_args().nth]
    home = os.path.realpath(os.path.expanduser(homefolder if homefolder else '~'))
    user = os.path.realpath(os.path.expanduser('~'))
    homename = os.path.basename(home)

    if os.path.isfile(home):
        os.environ['RH_CONFIG_FILENAME'] = home
    from butterfly import settings,core,webserver
    from rh_logger import logger

    port = port if port else settings.PORT
    logger.start_process("bfly", "Starting butterfly server on port {}".format(port), [port])
    logger.report_event("Datasources: " + ", ".join(settings.DATASOURCES),log_level=logging.DEBUG)
    logger.report_event("Allowed paths: " + ", ".join(settings.ALLOWED_PATHS),log_level=logging.DEBUG)
    c = core.Core()

    cat_name = ['root','experiments','samples','datasets','channels']
    new_kid = lambda n: {'kids': [], 'name': n}
    path_root = [new_kid(homename)]
    for cat in cat_name:
        path_root.append(new_kid('root'))
        path_root[-1]['kids'].append(path_root[-2])
    path_root.reverse()

    def sourcer(tmp_path, my_path):
        try: c.create_datasource(tmp_path)
        except: return new_kid(my_path)
        source = c.get_datasource(tmp_path)
        return source.get_channel(tmp_path)

    def path_walk(root, parent):
        [fold,folds,files] = next(os.walk(root), [[]]*3)
        for my_path in folds+files:
            tmp_path = os.path.join(fold, my_path)
            myself = sourcer(tmp_path, my_path)
            parent['kids'].append(myself)
            if 'kids' in myself:
                myself = path_walk(tmp_path, myself)
                root_kid = new_kid(my_path)
                root_kid['kids'] = [k for k in myself['kids'] if 'kids' not in k]
                myself['kids'] = [k for k in myself['kids'] if 'kids' in k]
                if root_kid['kids']:
                    myself['kids'].append(root_kid)
                if len(myself['kids']) == 1:
                    myself['kids'] = myself['kids'][0]['kids']
                if not myself['kids']:
                    parent['kids'].pop()
        return parent

    def depth_walk(depth, parent):
        for kid in parent['kids']:
            return depth if 'kids' not in kid else depth_walk(depth+1,kid)

    def flat_walk(depth, parent):
        if 'kids' in parent:
            flat = False
            cat_kids = []
            kid_depth = depth+1
            for kid in parent['kids']:
                myself = flat_walk(kid_depth, kid)
                if 'kids' in myself:
                    cat_kids += myself['kids']
                if 'flat' in myself:
                    #parent['kids'].remove(myself)
                    flat = True
            #if cat_kids and flat:
                #parent['kids'] += cat_kids
            if not flat and cat_kids and kid_depth >= len(cat_name):
                parent['flat'] = True
                parent['fat'] = [k['name'] for k in cat_kids]
        return parent

    def cat_walk(depth, parent):
        if 'kids' in parent:
            for kid in parent['kids']:
                cat_walk(depth+1, kid)
            cat = cat_name[(depth)%len(cat_name)]
            parent[cat] = parent['kids']
            del parent['kids']
            return parent[cat]
        return parent

    experiments = settings.bfly_config.setdefault('experiments',[])
    if homefolder and os.path.isdir(home):
        path_tree = path_walk(home, path_root[-1])
        min_depth = min(depth_walk(0, path_tree), len(cat_name)-1)
        path_tree = flat_walk(0, path_root[min_depth])
        #exp_tree = cat_walk(0, path_root[min_depth+1])
        #experiments += exp_tree[0]['experiments']
        exp_tree = path_tree
        kapow = open(os.path.join(user,'bfly_indexed.yaml'),'w')
        kapow.write(yaml.dump(exp_tree))
        kapow.close()
    ws = webserver.WebServer(c, port)
    ws.start()


# Custom parsing of the args file


def convert_arg_line_to_args(arg_line):
    for arg in re.split(''' (?=(?:[^'"]|'[^']*'|"[^"]*")*$)''', arg_line):
        if not arg.strip():
            continue
        yield arg.strip('\'\"')


def parseNumRange(num_arg):
    match = re.match(r'(\d+)(?:-(\d+))?$', num_arg)
    if not match:
        raise argparse.ArgumentTypeError(
            "'" + num_arg + "' must be a number or range (ex. '5' or '0-10').")
    start = match.group(1)
    end = match.group(2) or match.group(1)
    step = 1
    if end < start:
        step = -1
    return list(range(int(start), int(end) + step, step))


def query():
    from butterfly import core
    from rh_logger import logger, ExitCode
    logger.start_process("bquery", "Starting butterfly query")
    c = core.Core()

    # Parser for command-line arguments - to be incorporated separately in a
    # client-side tool
    parser = argparse.ArgumentParser(
        description='Returns cutout of requested volume from a given EM stack',
        fromfile_prefix_chars='@',
        add_help=False)
    parser.convert_arg_line_to_args = convert_arg_line_to_args

    # Argument group for input/output paths
    paths = parser.add_argument_group('Paths')
    paths.add_argument('-h', '--help', action='help', help=argparse.SUPPRESS)
    paths.add_argument('datapath', help='Path to EM stack')
    paths.add_argument(
        '--output',
        metavar='filename',
        help='Output file name (with extension), '
             'use sprintf format for multiple slices',
        required=True)

    # Argument group for information about requested volume
    v_inf = parser.add_argument_group('Requested volume')
    v_inf.add_argument(
        '--start',
        nargs=3,
        type=int,
        metavar=(
            'X',
            'Y',
            'Z'),
        help='Starting coordinates of the requested volume',
        required=True)
    v_inf.add_argument(
        '--size',
        nargs=3,
        type=int,
        metavar=(
            'X',
            'Y',
            'Z'),
        help='Size of the requested volume',
        required=True)
    v_inf.add_argument(
        '--zoom',
        nargs='?',
        type=int,
        default=0,
        metavar='level',
        help='MIP map level, 0 is default')

    # Hidden argument group for parameters - temporary for now! Will not be on
    # client, and will be optional on server
    d_inf = parser.add_argument_group()
    # EM stack filenames in sprintf format
    d_inf.add_argument('--filename', help=argparse.SUPPRESS, required=True)
    # Folder names for each vertical slice in sprintf format
    d_inf.add_argument('--folderpaths', help=argparse.SUPPRESS, required=True)
    d_inf.add_argument(
        '--x_ind',
        nargs='+',
        type=parseNumRange,
        help=argparse.SUPPRESS,
        required=True)  # Row indices of the filenames
    d_inf.add_argument(
        '--y_ind',
        nargs='+',
        type=parseNumRange,
        help=argparse.SUPPRESS,
        required=True)  # Column indices of the filenames
    d_inf.add_argument(
        '--z_ind',
        nargs='+',
        type=parseNumRange,
        help=argparse.SUPPRESS,
        required=True)  # Slice indices of the filenames
    d_inf.add_argument(
        '--blocksize',
        nargs=2,
        type=int,
        help=argparse.SUPPRESS,
        required=True)  # Tile size of each image (X, Y)

    args = parser.parse_args()
    # Paths and filenames for the current image set
    datapath = args.datapath
    # datapath = '/Volumes/DATA1/P3/'
    # datapath = '/home/e/Documents/Data/P3/'

    filename = args.filename
    folderpaths = args.folderpaths

    # Tile and slice index ranges - the list comprehensions can be understood
    # as nested for loops to flatten list
    z_ind = [number for sublist in args.z_ind for number in sublist]
    y_ind = [number for sublist in args.y_ind for number in sublist]
    x_ind = [number for sublist in args.x_ind for number in sublist]
    indices = (x_ind, y_ind, z_ind)

    # Requested volume (coordinates are for the entire current image set)
    start_coord = args.start
    vol_size = args.size
    zoom_level = args.zoom

    # In the case of regular image stacks we manually input paths
    c.create_datasource(datapath)
    ris = c._datasources[datapath]
    ris.load_paths(folderpaths, filename, indices)

    # Temporary input of blocksize, should be able to grab from index in the
    # future
    ris.blocksize = args.blocksize

    # Grab the sample volume
    volume = c.get(datapath, start_coord, vol_size, w=zoom_level)

    if vol_size[2] == 1:
        # Is there a better way to catch errors?
        try:
            cv2.imwrite(args.output, volume[:, :, 0].astype('uint8'))
        except cv2.error:
            logger.report_exception()
            logger.end_process('Could not write image',
                               ExitCode.io_error)
            exit(-1)
    else:
        for i in range(vol_size[2]):
            try:
                cv2.imwrite(args.output % i, volume[:, :, i].astype('uint8'))
            except cv2.error:
                logger.report_exception()
                logger.end_process('Could not write image',
                                   ExitCode.io_error)
                exit(-1)

    logger.end_process("Wrote cutout with volume = %s" % str(volume.shape),
                       ExitCode.success)
