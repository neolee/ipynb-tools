import argparse
from configparser import ConfigParser
from pathlib import Path
from distutils.dir_util import copy_tree
from itertools import chain
from datetime import datetime

from redact import redact


def process(source, dest, ts):
    p = Path(source).absolute()
    for f1 in chain(p.glob('[!.]*.ipynb'), p.glob('**/[!.]*/*.ipynb')):
        if f1.stat().st_mtime <= ts: continue

        print(f'[INFO] processing {f1}...')
        rpath = f1.relative_to(p)
        f2 = Path(dest).absolute() / rpath
        d = f2.parent
        d.mkdir(parents=True, exist_ok=True)
        redact(f1, f2)


def copy_assets(source, dest):
    p = Path(source).absolute()
    for d1 in p.glob('**/assets'):
        if d1.is_dir():
            rpath = d1.relative_to(p)
            d2 = Path(dest).absolute() / rpath
            copy_tree(str(d1), str(d2))


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(
        description='Processing notebooks to redact all code cells.')
    arg_parser.add_argument(
        'config',
        metavar='config',
        type=str,
        nargs='?',
        default='test',
        help='config name, file <config>.ini should exist with proper info')
    arg_parser.add_argument(
        '-f', '--force',
        action='store_true',
        help='force processing all notebooks, ignore the timestamps')
    arg_parser.add_argument(
        '--assets',
        action='store_true',
        help='copy all assets')
    args = arg_parser.parse_args()

    config_file = f'{args.config}.ini'
    config = ConfigParser()
    config.read(config_file)
    source = config['path']['source']
    dest = config['path']['dest']

    if args.assets: copy_assets(source, dest)

    ts = config['timestamp'].getfloat('lastest', fallback=0)
    if args.force: ts = 0

    process(source, dest, ts)

    config['timestamp']['lastest'] = str(datetime.now().timestamp())
    with open(config_file, 'w') as cf:
        config.write(cf)
