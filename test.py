#! /usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import time
import random
import itertools
from nasa_wildfires import get_modis, get_viirs_suomi, get_viirs_noaa, options


class NasaWildfiresUnitTest(unittest.TestCase):

    def test_modis(self):
        get_modis()
        combinations = random.sample(list(itertools.product(options.REGION_DICT.keys(), options.TIME_RANGE)), 5)
        for c in combinations:
            time.sleep(1)
            get_modis(*c)

    def test_viirs_suomi(self):
        get_viirs_suomi()
        combinations = random.sample(list(itertools.product(options.REGION_DICT.keys(), options.TIME_RANGE)), 5)
        for c in combinations:
            time.sleep(1)
            get_viirs_suomi(*c)

    def test_viirs_noaa(self):
        get_viirs_noaa()
        combinations = random.sample(list(itertools.product(options.REGION_DICT.keys(), options.TIME_RANGE)), 5)
        for c in combinations:
            time.sleep(1)
            get_viirs_noaa(*c)


if __name__ == '__main__':
    unittest.main()
