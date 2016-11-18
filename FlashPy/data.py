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
        self.contents   = h5py.File(filename)
        self.leaves     = self._get_leaves(self.contents['refine level'][:])
        self.ndim       = self.contents['coordinates'][:].shape[-1] # get the dims  
        
    def get_keys(self):
        """Recover the list of keys from the file"""
        keys = [key for key in self.contents.keys()]

        return keys

    def get_values(self, key, unpack=False):
        """Recovers the values stored in the dataset associated with the provided
        key.
        
        Parameters
        ------------
        key
            The key of the dataset to retrieve.
        
        unpack
            Whether or not to unpack the dataset into the shape of the actual
            simulation box. Default: False.
        
        Returns
        ------------
        dataset
            A numpy.ndarray containing the values from the nominated dataset.
        """
        dataset = self.contents[key][:][self.leaves]
        
        
        if unpack:
            dataset = self._unpack_data(dataset)
        
        return dataset

    def _unpack_data(self, data_array):
        """Unpacks a 4D dataset into the 'correct' 3D shape associated with the 
        size of the simulation box. This currently assumes that the simulation box
        is cubic, with the same number of blocks in each direction. 
        
        Parameters
        ------------
        data_array
            The dataset to unpack.
        
        Returns
        ------------
        data_array
            The same values unpacked. 
        """
        ncells  = data_array.shape[0]
        nblocks = round(ncells**(1/3)) 
        
        data_array = numpy.concatenate(
                    [numpy.concatenate(
                    [numpy.concatenate(
                        data_array[j*nblocks**2+i*nblocks:j*nblocks**2+(i+1)*nblocks], axis=2)
                        for i in range(nblocks)], axis=1) for j in range(nblocks)], axis=0)
        
        
        return data_array

    def _get_leaves(self, ref_levels):
        
        
        leaves = []
        for index in range(0, len(ref_levels)-1):
            if ref_levels[index+1] > ref_levels[index]:
                continue 
            elif ref_levels[index+1] <= ref_levels[index]:
                leaves.append(index)
                
        leaves.append(index+1)
        
        leaves = numpy.array(leaves)
        
        return leaves



