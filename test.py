#! /usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from nasa_wildfires import get_modis, get_viirs_suomi, get_viirs_noaa


class NasaWildfiresUnitTest(unittest.TestCase):

    def test_modis(self):
        get_modis()

    def test_viirs_suomi(self):
        get_viirs_suomi()

    def test_viirs_noaa(self):
        get_viirs_noaa()


if __name__ == '__main__':
    unittest.main()
