"""Offline tests of the optional ``get`` argument, with a fake request function."""

import pytest
import requests

import nasa_wildfires
from nasa_wildfires import NASADataError, NASAError, Satellite, fetch

from .conftest import FakeResponse


class Recorder:
    """A fake request function that plays back replies and remembers each call."""

    def __init__(self, *replies) -> None:
        self.replies = list(replies)
        self.urls: list[str] = []
        self.timeouts: list[float] = []

    def __call__(self, url: str, *, timeout: float) -> FakeResponse:
        self.urls.append(url)
        self.timeouts.append(timeout)
        reply = self.replies[min(len(self.urls), len(self.replies)) - 1]
        if isinstance(reply, Exception):
            raise reply
        return reply


@pytest.fixture
def good(sample_csv):
    """A good reply."""
    return FakeResponse(sample_csv("modis.csv"))


@pytest.fixture
def no_requests(monkeypatch):
    """Fail the test if the package falls back to ``requests.get``."""

    def refuse(*args, **kwargs):
        raise AssertionError("requests.get should not be called")

    monkeypatch.setattr(fetch.requests, "get", refuse)


def test_types_are_exported():
    """The two types are part of the public package."""
    assert nasa_wildfires.Fetcher is fetch.Fetcher
    assert nasa_wildfires.Reply is fetch.Reply
    assert {"Fetcher", "Reply"} <= set(nasa_wildfires.__all__)


def test_function_is_used_instead_of_requests(no_requests, good):
    """The caller's function makes the request, and requests is never used."""
    get = Recorder(good)
    data = nasa_wildfires.get_hotspots("modis", get=get)
    assert len(data["features"]) == 3
    assert len(get.urls) == 1
    assert get.urls[0].startswith("https://firms")


def test_records_use_the_function(no_requests, good):
    """Typed records can use the caller's function too."""
    records = nasa_wildfires.get_hotspot_records("modis", get=Recorder(good))
    assert len(records) == 3


def test_timeout_is_passed_through(no_requests, good):
    """The timeout reaches the caller's function, 60 seconds by default."""
    get = Recorder(good, good)
    nasa_wildfires.get_hotspots("modis", get=get)
    nasa_wildfires.get_hotspots("modis", timeout=5, get=get)
    assert get.timeouts == [60.0, 5]


def test_fails_over_between_servers(no_requests, good):
    """After a failure the next try asks NASA's other server."""
    get = Recorder(FakeResponse(status_code=503), good)
    nasa_wildfires.get_hotspots("modis", get=get)
    assert {url.split("/")[2] for url in get.urls} == set(fetch.DOMAINS)


@pytest.mark.parametrize(
    "failure",
    [
        requests.ConnectionError("no route"),
        requests.Timeout("too slow"),
        FakeResponse(status_code=500),
        FakeResponse(status_code=429),
    ],
)
def test_retries_then_succeeds(no_requests, good, failure):
    """A network problem or a busy server is tried again."""
    get = Recorder(failure, good)
    assert len(nasa_wildfires.get_hotspots("modis", get=get)["features"]) == 3
    assert len(get.urls) == 2


def test_gives_up_with_nasa_error(no_requests):
    """After every try fails a NASAError says what happened last."""
    get = Recorder(FakeResponse(status_code=503))
    with pytest.raises(NASAError, match="status 503") as caught:
        nasa_wildfires.get_hotspots("modis", get=get)
    assert caught.value.status_code == 503
    assert len(get.urls) == 4


def test_not_found_is_not_retried(no_requests):
    """A 404 fails on the first try."""
    get = Recorder(FakeResponse(status_code=404))
    with pytest.raises(NASAError, match="404"):
        nasa_wildfires.get_hotspots("modis", get=get)
    assert len(get.urls) == 1


def test_other_request_error_becomes_nasa_error(no_requests):
    """A requests error that is not a network problem fails right away."""
    get = Recorder(requests.exceptions.InvalidURL("bad"))
    with pytest.raises(NASAError, match="failed"):
        nasa_wildfires.get_hotspots("modis", get=get)
    assert len(get.urls) == 1


def test_reply_without_ok_attribute(no_requests, good):
    """A reply needs only status_code and content, not requests' ``ok``."""

    class Bare:
        status_code = 200
        content = good.content

    assert (
        len(nasa_wildfires.get_hotspots("modis", get=Recorder(Bare()))["features"]) == 3
    )


def test_bad_file_is_a_data_error(no_requests):
    """A reply that is not a hotspot file raises NASADataError."""
    with pytest.raises(NASADataError):
        nasa_wildfires.get_hotspots("modis", get=Recorder(FakeResponse(b"<html>")))


def test_default_still_uses_requests(fake_nasa):
    """With no function, requests.get is used as before."""
    assert len(nasa_wildfires.get_hotspots("modis")["features"]) == 3
    assert len(fake_nasa.urls) == 1


@pytest.mark.parametrize(
    ("func", "satellite"),
    [
        (nasa_wildfires.get_modis, Satellite.MODIS),
        (nasa_wildfires.get_viirs_suomi, Satellite.VIIRS_SUOMI),
        (nasa_wildfires.get_viirs_noaa, Satellite.VIIRS_NOAA),
        (nasa_wildfires.get_viirs_noaa21, Satellite.VIIRS_NOAA21),
    ],
)
def test_old_functions_accept_get(no_requests, good, func, satellite):
    """The older satellite functions take get and timeout too."""
    get = Recorder(good)
    data = func("canada", "48h", get=get, timeout=9)
    assert data == nasa_wildfires.get_hotspots(
        satellite, "canada", "48h", get=Recorder(good)
    )
    assert get.timeouts == [9]
    assert satellite.csv_path("Canada", "48h") in get.urls[0]
