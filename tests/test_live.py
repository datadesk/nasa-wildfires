"""Tests that call NASA's real website.

They are skipped unless you ask for them with ``make test-live`` (or
``uv run pytest -m live``), because they are slow and fail whenever NASA is
down.
"""

import itertools
import random
import time

import pytest

from nasa_wildfires import get_modis, get_viirs_noaa, get_viirs_suomi, options

pytestmark = pytest.mark.live

COMBO_LIST = list(
    itertools.product(options.REGION_DICT.keys(), options.TIME_RANGE_LIST)
)


@pytest.mark.parametrize(
    "func", [get_modis, get_viirs_suomi, get_viirs_noaa], ids=lambda f: f.__name__
)
def test_live_download(func):
    """Download the default and a few random region and time combinations."""
    func()
    for combo in random.sample(COMBO_LIST, 5):
        time.sleep(1)
        func(*combo)
