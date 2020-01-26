#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup script for hpccm."""

import os

from setuptools import find_packages
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

# Get the package version from hpccm/version.py
version = {}
with open(os.path.join(here, 'jhcspawner', 'version.py')) as fp:
    exec(fp.read(), version)

# Get the long description from the README file
with open(os.path.join(here, 'README.md')) as fp:
    long_description = fp.read()

setup(
    name='jhcspawner',
    version=version['__version__'],
    description='Jupyter Hybrd Cloud Spawner',
    long_description=long_description,
    long_description_content_type='text/markdown',
    maintainer='Sean Brisbane',
    maintainer_email='sean.brisbane@securelinx.com',
    license='Apache License Version 2.0',
    url='https://github.com/brisbane/jupyter_hybridcloud_spawner',
    packages=find_packages(),
    classifiers=[
      "License :: OSI Approved :: Apache Software License",
      "Programming Language :: Python :: 3",
      "Programming Language :: Python :: 3.4",
      "Programming Language :: Python :: 3.5",
      "Programming Language :: Python :: 3.6"
    ],
)
