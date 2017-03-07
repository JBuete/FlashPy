#!/usr/bin/env python3

import h5py
import numpy
import logging


def gen_async_data():

    logging.info("Generating async_example_data")

    # first we want a test case that's of the shape (4, 128, 64, 64)
    shape = (4, 128, 64, 64)
    with h5py.File("tests/async_example_data") as data:
        # clear all of the information from the file first
        data.clear()

        # now add the information
        info = numpy.ones(shape)

        data.create_dataset("data", shape=shape, data=info)


if __name__ == '__main__':
    logging.basicConfig(format="[%(levelname)s] %(message)s")

    gen_async_data()
