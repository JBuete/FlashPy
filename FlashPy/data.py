#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import h5py
import numpy
import re
import logging


class Data():
    """The basic datatype for the FlashPy module.
    It will provide the basis for the interface between
    the user and the analysis.
    """

    def __init__(self, filename):
        self.contents = h5py.File(filename)

        if 'refine level' in self.contents:
            self.leaves = self._get_leaves(self.contents['refine level'][:])

        if 'coordinates' in self.contents:
            self.ndim = self.contents['coordinates'][:].shape[-1]  # get the dims

        self.index = self._get_index()

        self.properties = self._get_properties()

        self.user_fields = {}

    def _get_properties(self):
        """Creates a dictionary of the simulation parameters and scalars"""
        # create the returnable
        properties = {}

        # first we want to run through all of the known properties
        if 'integer runtime parameters' in self.contents:
            properties.update({name.rstrip().decode('utf-8'): value for name, value
                               in self.contents['integer runtime parameters'][:]})

        if 'real runtime parameters' in self.contents:
            properties.update({name.rstrip().decode('utf-8'): value for name, value
                               in self.contents['real runtime parameters'][:]})

        if 'string runtime parameters' in self.contents:
            properties.update({name.rstrip().decode('utf-8'): value.rstrip().decode('utf-8') for name, value
                               in self.contents['string runtime parameters'][:]})

        if 'integer scalars' in self.contents:
            properties.update({name.rstrip().decode('utf-8'): value for name, value
                               in self.contents['integer scalars'][:]})

        if 'real scalars' in self.contents:
            properties.update({name.rstrip().decode('utf-8'): value for name, value
                               in self.contents['real scalars'][:]})

        if 'string scalars' in self.contents:
            properties.update({name.rstrip().decode('utf-8'): value.rstrip().decode('utf-8') for name, value
                               in self.contents['string scalars'][:]})

        return properties

    def _get_index(self):
        """Recovers the index of the sorted block list"""

        # first load the coordinates into memory, only the leaves
        coords = self.contents['coordinates'][:][self.leaves]

        # now calculate the index
        index = numpy.lexsort((coords[:, 2], coords[:, 1], coords[:, 0]))

        return index

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
        if type(key) == float:
            return key

        # first check if the key is actually one of the properties
        if key in self.properties.keys():
            logging.warning(
                "Please use the properties attribute to find runtime parameters in future")
            return self.properties[key]

        # if not one of the properties then try and grab some values
        if key in self.user_fields.keys():
            dataset = self.user_fields[key][self.leaves]
        else:
            try:
                dataset = self.contents[key][:][self.leaves]
            except KeyError:
                logging.error("{} is not a valid key".format(key))
                return None

        if unpack:
            dataset = self._unpack_data2(dataset)

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

        # first sort the data_array by the coordinates of each of the blocks
        data_array = data_array[self.index]

        # then get the number of blocks on each axis (assumes cubic)
        ncells = data_array.shape[0]
        nblocks = round(ncells**(1 / 3))

        # sort the data_array into the new shape
        data_array = numpy.concatenate(
            [numpy.concatenate(
                [numpy.concatenate(
                    data_array[j * nblocks**2 + i * nblocks:j *
                               nblocks**2 + (i + 1) * nblocks], axis=0
                ) for i in range(nblocks)], axis=1
            ) for j in range(nblocks)], axis=2
        )

        return data_array

    def _unpack_data2(self, data_array):
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

        # first sort the data_array by the coordinates of each of the blocks
        data_array = data_array[self.index]

        # get the shape of the data
        shape = data_array.shape

        # based on if nblocks is cubic, square, or neither, we need to treat
        # the unpacking differently
        ncells = shape[1:]

        max_dim = max(ncells)

        no_max_dims = ncells.count(max_dim)

        if no_max_dims == 3:  # all dimensions are the same
            nblocks = round(shape[0]**(1 / 3))

            # sort the data_array into the new shape
            data_array = numpy.concatenate(
                [numpy.concatenate(
                    [numpy.concatenate(
                        data_array[j * nblocks**2 + i * nblocks:j *
                                   nblocks**2 + (i + 1) * nblocks], axis=0
                    ) for i in range(nblocks)], axis=1
                ) for j in range(nblocks)], axis=2
            )
        elif no_max_dims == 2:  # only one of the dimensions is different

            # first find out which dimension isn't correct
            for dim in len(ncells):
                if ncells[dim] != max_dim:  # this is the one we're looking for
                    break

            # now we can perform the reshaping
            data_array = numpy.concatenate(data_array, axis=dim)

        elif no_max_dims == 1:  # two of the dimensions are different
            # we are going to assume the other two dimensions are the same
            if ncells[1] != max_dim:
                nbs = int(max_dim / ncells[1])
            else:
                nbs = int(max_dim / ncells[2])

            data_array = numpy.concatenate(
                numpy.concatenate(
                    [data_array[i * nbs:(i + 1) * nbs] for i in range(nbs)], axis=3
                ), axis=1
            )

        else:
            raise ValueError("None of the dimensions are the maximum?")

        return data_array

    def _get_leaves(self, ref_levels):

        leaves = []
        for index in range(0, len(ref_levels) - 1):
            if ref_levels[index + 1] > ref_levels[index]:
                continue
            elif ref_levels[index + 1] <= ref_levels[index]:
                leaves.append(index)

        leaves.append(index + 1)

        leaves = numpy.array(leaves)

        return leaves

    def _map_to_uniform(self, array):
        """Takes a given dataset from the hdf5 file and maps it onto a uniform
        grid. This is used for 'true' AMR data which doesn't necessarily have
        uniform resolution throughout the simulation boundaries.
        """

        # first figure out the highest resolution avaliable
        nxb = self.properties['nxb']
        nyb = self.properties['nyb']
        nzb = self.properties['nzb']

        # the highest refinement should be contained as a leaf
        # node so just take that, don't need to index by the leaves first

        # resolution is given by
        if 'processor number' in self.contents:  # we are dealing with amr
            max_ref_level = numpy.max(self.contents['refine level'][:])
            max_res_x = nxb * 2**(ref_level - 1) * self.properties['nblockx']
            max_res_y = nyb * 2**(ref_level - 1) * self.properties['nblocky']
            max_res_z = nzb * 2**(ref_level - 1) * self.properties['nblockz']

            block_filter = self.contents['refine level'][self.leaves] == max_ref_level

        else:  # otherwise this is a uniform grid
            max_res_x = nxb * self.properties['iprocs']
            max_res_y = nyb * self.properties['jprocs']
            max_res_z = nzb * self.properties['kprocs']

        return final_data

    def _convert_terms(terms):
        """
        _convert_terms(terms)

        Converts any potential floats in the terms to floats
        """
        for i in range(len(terms)):
            try:
                terms[i] = float(terms[i])
            except ValueError:
                continue
        return terms

    def create_field(self, name, expr):
        """
        create_field(name, expr)

        Allows the user to create a new field from existing fields for use
        in analysis. The field will be called `name` and is defined by the
        expression `expr`.

        Parameters
        ----------
        name : str
            The name of the field to be added.
        expr : list of str
            The definition of the field. The definition must use pre-existing
            fields and standard mathematical symbols (`*`, `-`, `/`)

        Notes
        -----
        The expression used for the definition of the field has to be in a
        specific format. In order to simplify the code required to parse the
        expression, the expression must be a list of clusters of multiplication
        and devision that are then added together.

        For example, the expression "a + b*c + 1/d" would be formatted as
        follows:

            ["a", "b*c", "1/d"]

        Subtraction is included, however it requires a `-` inside the term to
        be subtracted. This is equivalent to the fact that "a - b" is "a + -b",
        and would be defined as follows:

            ["a", "-b"]

        Examples
        --------
        Creating a velocity vector

        >>> data = FlashPy.Data(my_data)
        >>> data.create_field("vel", ["velx*velx", "vely * vely", "velz *velz"])

        Note that the whitespace in the terms within the expression doesn't
        matter, so they can be formatted however is most visually clear.

        We can then use the `vel` field to make a momentumn field

        >>> data.create_field("mom", ["dens*vel"])
        """

        if name in self.get_keys() or name in self.user_fields.keys():
            raise ValueError("Supplied name is already an existing field")

        if expr == []:  # there wasn't a supplied expression
            raise ValueError("There is no supplied expression")

        # define the pattern that we use for the regex
        pattern = r"([a-z]+|[0-9\.]+|[\*\-/])"

        # now we want to parse the expression
        value = 0  # this is the holder
        for part in expr:

            terms = re.findall(pattern, part)

            # if the first part is `-` then we need to negate the values
            if terms[0] == '-':
                scale = -1
                terms = terms[1:]

            # convert any terms that are floats
            terms = _convert_terms(terms)

            # now extract the first value using the necessary scale
            temp = scale * self.get_values(terms[0])

            # every second part of the term should be an operator
            # if not we have an invalid expression
            for i in range(1, len(terms), 2):
                if terms[i] == "*":
                    temp *= self.get_values(terms[i + 1])
                elif terms[i] == '/':
                    temp /= self.get_values(terms[i + 1])
                else:
                    raise ValueError("The provided expression is not valid")

            value += temp

        # now define the field
        self.user_fields[name] = value
