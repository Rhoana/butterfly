import re
import os
import cv2
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

    def sourcer(fold, child, pointer):
        tmp_path = os.path.join(fold, child)
        try: c.create_datasource(tmp_path)
        except: return path_walk(tmp_path, pointer)
        pointer.pop('kids', None)
        source = c.get_datasource(tmp_path)
        return source.get_channel(tmp_path)

    def path_walk(root, parent):
        [fold,folds,files] = next(os.walk(root), [[]]*3)
        for my_path in folds+files:
            my_name = os.path.basename(my_path)
            myself = new_kid(my_name)
            parent['kids'].append(myself)
            myself.update(sourcer(fold, my_path, myself))
            if 'kids' in myself:
                my_kids = myself['kids']
                mv_key = ['kids' not in k for k in my_kids]
                mv_val = [my_kids[ki] for ki in np.where(mv_key)[0]]
                if not my_kids: parent['kids'].pop()
                if any(mv_key) and not all(mv_key):
                    new_group = new_kid(my_name)
                    new_group['channels'] = True
                    for mover in mv_val:
                        new_group['kids'].append(mover)
                        my_kids.remove(mover)
                    my_kids.append(new_group)
                if my_kids and all(mv_key):
                    myself['channels'] = True
        return {}

    def depth_walk(depth, parent):
        for kid in parent['kids']:
            return depth if 'channels' in kid else depth_walk(depth+1,kid)

    def flat_walk(depth, parent, myself):
        my_kids = [kid for kid in myself['kids']]
        for kid in my_kids:
            kid_depth = depth+1
            if 'channels' not in kid:
                cat = cat_name[(kid_depth)%len(cat_name)]
                flat_walk(kid_depth, myself, kid)
                kid['cat'] = cat
            if 'channels' in kid:
                kid['channels'] = kid['kids']
                del kid['kids']
        if depth+1 >= len(cat_name):
            parent['kids']+= myself['kids']
            parent['kids'].remove(myself)

    def cat_walk(parent):
        if 'kids' in parent:
            for kid in parent['kids']:
                new_cat = cat_walk(kid)
                if new_cat:
                    return new_cat
                if 'kids' in kid and 'cat' in kid:
                    kid[kid['cat']] = kid['kids']
                    del kid['kids']
                    del kid['cat']
                if 'experiments' in kid:
                    return kid
        return False

    experiments = settings.bfly_config.setdefault('experiments',[])
    if homefolder and os.path.isdir(home):
        path_walk(home, path_root[-1])
        min_depth = min(depth_walk(0, path_root[-1]),len(cat_name)-2)
        print 'important: ' + str(min_depth)
        flat_walk(0, path_root[min_depth], path_root[min_depth+1])
        exp_tree = cat_walk(path_root[min_depth+1])
        experiments += exp_tree['experiments']
        import yaml
        kapow = open('/home/harvard/kapow.yaml','w')
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
