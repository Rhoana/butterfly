#!/usr/bin/env python
from setuptools import find_packages
from setuptools import setup

VERSION = 2.0
INSTALL_REQ = [
    'h5py>=2.6.0',
    'numpy>=1.12.0',
    'tornado>=4.4.2',
    'futures>=3.0.5',
    'pyaml>=16.12.2',
    'tifffile>=0.11.1',
    'pymongo>=3.4.0',
    'rtree>=0.8.3',
]

setup(
    version=VERSION,
    name='bfly',
    author='Daniel Haehn',
    packages=find_packages(),
    author_email='haehn@seas.harvard.edu',
    url="https://github.com/Rhoana/butterfly",
    description="butterfly dense image server",
    # Installation requirements
    install_requires= INSTALL_REQ,
    # Allows command line execution
    entry_points=dict(console_scripts=[
        'bfly = bfly.__main__:bfly'
    ])
)
