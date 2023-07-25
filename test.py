#! /usr/bin/env python
import itertools
import random
import time
import unittest

from rich import print

from nasa_wildfires import get_modis, get_viirs_noaa, get_viirs_suomi, options

COMBO_LIST = list(
    itertools.product(options.REGION_DICT.keys(), options.TIME_RANGE_LIST)
)


class NasaWildfiresUnitTest(unittest.TestCase):
    """Test the nasa_wildfires package."""

    def test_modis(self):
        """Test the MODIS function."""
        print("Testing MODIS")
        get_modis()
        combinations = random.sample(COMBO_LIST, 5)
        for c in combinations:
            print(f"Testing MODIS with {c}")
            time.sleep(1)
            get_modis(*c)

    def test_viirs_suomi(self):
        """Test the VIIRS Suomi function."""
        print("Testing VIIRS Suomi")
        get_viirs_suomi()
        combinations = random.sample(COMBO_LIST, 5)
        for c in combinations:
            print(f"Testing VIIRS Suomi with {c}")
            time.sleep(1)
            get_viirs_suomi(*c)

    def test_viirs_noaa(self):
        """Test the VIIRS NOAA function."""
        print("Testing VIIRS NOAA")
        get_viirs_noaa()
        combinations = random.sample(COMBO_LIST, 5)
        for c in combinations:
            print(f"Testing VIIRS NOAA with {c}")
            time.sleep(1)
            get_viirs_noaa(*c)


if __name__ == "__main__":
    unittest.main()
