#!/usr/bin/env python
import os

from setuptools import setup, find_packages

VERSION = 0.1
version = os.path.join('butterfly', '__init__.py')
execfile(version)

README = open('README.md').read()

setup(
    name='butterfly',
    version=VERSION,
    packages=find_packages(),
    author='Daniel Haehn',
    author_email='haehn@seas.harvard.edu',
    url="https://github.com/Rhoana/butterfly",
    description="butterfly",
    long_description=README,
    install_requires=[
        "argparse>=1.4.0",
        "numpy>=1.9.3",
        "h5py>=2.6.0",
        "scipy>=0.16.0",
        "tornado>=4.3",
    ],
    entry_points=dict(console_scripts=[
        'bfly = butterfly.cli:main',
        'bfly_query = butterfly.cli:query',
    ]),
    zip_safe=False
)
