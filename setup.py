#!/usr/bin/env python
import os

from setuptools import setup, find_packages

VERSION = 0.2
version = os.path.join('butterfly', '__init__.py')
execfile(version)

README = open('README.md').read()

butterfly_package_data = [
    os.path.join("static", filename)
    for filename in os.listdir(os.path.join("butterfly", "static"))
    if any([filename.endswith(ext) for ext in ".html", ".js"])] + [
    os.path.join("static", "images", filename)
    for filename in os.listdir(os.path.join("butterfly", "static", "images"))
    if filename.endswith(".png")]

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
        "numpy>=1.9.3",
        "h5py>=2.6.0",
        "scipy>=0.16.0",
        "tornado>=4.3",
        "rh_logger>=2.0.0",
        "rh_config>=1.0.0"],
    dependency_links=[
        "https://github.com/Rhoana/rh_logger/tarball/master#egg=rh_logger-2.0.0",
        "https://github.com/Rhoana/rh_config/tarball/master#egg=rh_config-1.0.0"
    ],
    entry_points=dict(console_scripts=[
        'bfly = butterfly.cli:main',
        'bfly_query = butterfly.cli:query',
    ]),
    package_data=dict(butterfly=butterfly_package_data),
    zip_safe=False
)
