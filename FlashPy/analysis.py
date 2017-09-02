#!/bin/env/python3
# -*- coding: utf-8 -*-

import numpy


def density_spectrum():

    pass


def get_profile(data_set, quantity, process='mean', centre=(0, 0, 0), radius=0,
                sqrt=False):
    """Generates a 1d profile for the selected quantity for the given data_set.
    The profile has (n - 1) data points, where n is half the number of cells
    across the smallest width of the box

    Arguments
    ---------

    process = [mean, max, min]

    """

    # first get the width of the box that we need
    x_width = data_set.properties['xmax'] - data_set.properties['xmin']

    # grab the data, this will also give us the number of cells to use
    data = data_set.get_values(quantity, unpack=True)

    ncells = data.shape[-1]  # this is a stop gap, need to figure how to adapt

    # next we want to make the radii information
    cell_width = x_width / ncells
    lower = 0.5 - ncells / 2
    upper = 1 - lower

    # this will make the cartesian distance things
    X, Y, Z = cell_width * numpy.mgrid[lower:upper, lower:upper, lower:upper]

    # offset by the provided centre
    X -= centre[1]
    Y -= centre[2]
    Z -= centre[0]

    # now the radius
    radii = numpy.sqrt(X**2 + Y**2 + Z**2)

    # now we can do the filtering
    if radius == 0:
        intervals = numpy.linspace(
            0, x_width / 2, ncells // 2)  # n - 1 intervals
    else:
        intervals = numpy.linspace(0, radius,
                                   (ncells * (2 / x_width * radius)) // 2)

    radius = intervals[:-1] + \
        (intervals[1] - intervals[0]) / 2  # centre of intervals
    values = numpy.empty(radius.shape)

    # check if we want to sqrt the data
    if sqrt:
        data = numpy.sqrt(data)

    # we also want to figure out the process that we're using
    if process == 'mean':
        proc = numpy.mean
    elif process == 'max':
        proc = numpy.max
    elif process == 'min':
        proc = numpy.min
    else:
        raise ValueError(
            "{} is not a process that can be used".format(process))

    for i in range(len(intervals) - 1):
        filtering = (radii <= intervals[i + 1]) & (radii >= intervals[i])

        values[i] = proc(data[filtering])

    return values, radius


def sphere():

    pass


def slice(data_set, quantity, position=0, face='xy'):
    """Returns a slice at the position along the axis perpendicular to the
    selected face
    """

    # import the data
    data = data_set.get_values(quantity, unpack=True)

    # first get the coordinate positions along the chosen axis
    if face == 'xy':
        coords = numpy.linspace(data_set.properties['zmin'],
                                data_set.properties['zmax'],
                                data.shape[0] + 1)
        coords = coords[:-1] + abs(coords[1] - coords[0]) / 2
    elif face == 'xz':
        coords = numpy.linspace(data_set.properties['ymin'],
                                data_set.properties['ymax'],
                                data.shape[2] + 1)
        coords = coords[:-1] + abs(coords[1] - coords[0]) / 2
    elif face == 'yz':
        coords = numpy.linspace(data_set.properties['xmin'],
                                data_set.properties['xmax'],
                                data.shape[1] + 1)
        coords = coords[:-1] + abs(coords[1] - coords[0]) / 2
    else:
        raise ValueError("{} is not a face that can be selected".format(face))

    # next we want to figure out where along that axis the slice is
    # this is the one just under it
    pos = numpy.where(coords >= position)[0][0] - 1

    # now grab that slice and the one after it and we'll weight the information
    cell_width = abs(coords[1] - coords[0])

    weight_1 = abs(position - coords[pos]) / cell_width
    weight_2 = 1 - weight_1  # the weights should sum to one

    slice_value = data[pos, :, :] * weight_1 + data[pos + 1, :, :] * weight_2

    return slice_value


def pdf(data_set, quantity, nbins, norm=True, range=None):
    """Generates a PDF of the chosen quantity for the provided data_set.
    Includes an optional variable, norm, which will signal whether the PDF
    should be normalised or not. The pdf will contain a number of points equal
    to nbins.
    """

    # extract the data
    data = data_set.get_values(quantity, unpack=True)

    # generate the pdf
    pdf, bin_edges = numpy.histogram(data, nbins, normed=norm, range=range)

    bins = bin_edges[:-1] + (bin_edges[1] - bin_edges[0]) / 2

    # now we can simply return this information
    return pdf, bins
