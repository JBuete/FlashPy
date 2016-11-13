# -*- coding: utf-8 -*-
#!/bin/env/python3 

import h5py
import numpy

class Data():
    """The basic datatype for the FlashPy module. 
    It will provide the basis for the interface between
    the user and the analysis.
    """

    def __init__(self, filename):
        self.contents = h5py.File(filename)

    def get_keys(self):
        keys = [key for key in self.contents.keys()]

        return keys

    def get_values(self, key):
        data = self.contents[key][:]

        return data



