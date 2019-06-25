#! /usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from nasa_wildfires import get_modis, get_viirs


class NasaWildfiresUnitTest(unittest.TestCase):

    def test_modis(self):
        get_modis()

    def test_viirs(self):
        get_viirs()


if __name__ == '__main__':
    unittest.main()
