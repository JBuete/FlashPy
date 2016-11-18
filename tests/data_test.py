# -*- coding: utf-8 -*-
#!/bin/env/python3 

from .context import FlashPy

import unittest
import numpy

class DataTestSuite(unittest.TestCase):
    """Basic tests for the Data object in FlashPy
    """

    def test_key(self):
        """Able to retrive keys from the file"""
        data = FlashPy.Data('tests/key_test')

        
        self.assertEqual(data.get_keys(), ['coordinates', 'ones', 'refine level'])

    def test_values(self):
        """Can retrieve values from the file"""
        data = FlashPy.Data('tests/key_test')
        
        self.assertTrue(numpy.array_equal(data.get_values('ones'), numpy.ones((128, 128, 128))))
        self.assertTrue(numpy.array_equal(data.get_values('coordinates'), numpy.ones((64, 3))))
            
        
    def test_leaves(self):
        data = FlashPy.Data("tests/amr_example_data")
        
        self.assertEqual(len(data.leaves), 4096)
        self.assertTrue(numpy.array_equal(data.leaves, numpy.where(data.get_values('refine level') == 5)[0]))

if __name__ == '__main__':
    unittest.main()
