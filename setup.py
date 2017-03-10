#!/usr/bin/env python
from setuptools import setup, find_packages
import os

VERSION = 2.0

setup(
    version=VERSION,
    name='butterfly',
    packages=['butterfly'],
    author='Daniel Haehn',
    author_email='haehn@seas.harvard.edu',
    url="https://github.com/Rhoana/butterfly",
    long_description=open('README.md').read(),
    description="butterfly dense image server",
    install_requires=[
        'h5py>=2.6.0',
        'numpy>=1.12.0',
        'unqlite>=0.5.3',
        'tornado>=4.4.2',
        'futures>=3.0.5',
        'pyaml>=16.12.2',
        'tifffile>=0.11.1',
        'opencv-python>=3.2.0.6'
    ],
    entry_points=dict(console_scripts=[
        'bfly = butterfly.butterfly:main'
    ])
)
