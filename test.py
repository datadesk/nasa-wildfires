#! /usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import time
from nasa_wildfires import get_modis, get_viirs_suomi, get_viirs_noaa, options


class NasaWildfiresUnitTest(unittest.TestCase):

    def test_modis(self):
        get_modis()
        for r in options.REGION_DICT.keys():
            time.sleep(1)
            for t in options.TIME_RANGE:
                time.sleep(1)
                get_modis(r, t)

    def test_viirs_suomi(self):
        get_viirs_suomi()
        for r in options.REGION_DICT.keys():
            time.sleep(1)
            for t in options.TIME_RANGE:
                time.sleep(1)
                get_viirs_suomi(r, t)

    def test_viirs_noaa(self):
        get_viirs_noaa()
        for r in options.REGION_DICT.keys():
            time.sleep(1)
            for t in options.TIME_RANGE:
                time.sleep(1)
                get_viirs_noaa(r, t)


if __name__ == '__main__':
    unittest.main()
