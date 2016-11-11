"""The setup file for FlashPy

This file is based on the setup.py found in https://github.com/pypa/sampleproject/

Jacob Buete 
2016
"""


# import the required functions
from setuptools import setup, find_packages
from codecs import open 
from os import path 


here = path.abspath(path.dirname(__file__))

# get the description from the README
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name = 'FlashPy',
    
    version = '0.0.1.dev1',
    
    description = 'A Python module for visualising and analysing HDF5 output files from FLASH simulations',

    long_description = long_description,

    url = 'https://github.com/JBuete/FlashPy',

    author = 'Jacob Buete',

    author_email = 'jacob.buete@gmail.com',

    license = 'MIT',

    classifiers=[
        'Development Status :: 1 - Planning',

        'Intended Audience :: Science/Research',

        'Topic :: Scientific/Engineering :: Physics',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    keywords = 'FLASH data hdf5 analysis visualisation',

    packages = ['FlashPy'],

    install_requires=[
        'h5py',
        'numpy',
        'matplotlib',
    ],

    package_dir={
        'FlashPy': 'FlashPy',    
    },

    package_data={
        'FlashPy': '../README.rst',    
    }
)

