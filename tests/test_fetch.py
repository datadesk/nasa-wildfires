"""Offline tests of timeouts, retries, fallback and errors, with fake replies."""

import pytest
import requests
from click.testing import CliRunner

import nasa_wildfires
from nasa_wildfires import NASADataError, NASAError, fetch
from nasa_wildfires.cli import cmd

from .conftest import FakeResponse


@pytest.fixture
def script(monkeypatch):
    """Make ``requests.get`` play back a list of replies, one for each call.

    An item that is an exception is raised, and any other item is returned.
    Returns an object with the ``urls`` that were asked for and the ``kwargs``
    of the last call.
    """

    class Script:
        replies: list = []
        urls: list[str] = []
        kwargs: dict = {}

    play = Script()
    play.urls = []

    def get(url, **kwargs):
        play.urls.append(url)
        play.kwargs = kwargs
        reply = play.replies[len(play.urls) - 1]
        if isinstance(reply, Exception):
            raise reply
        return reply

    monkeypatch.setattr(fetch.requests, "get", get)
    return play


@pytest.fixture
def good(sample_csv):
    """A good reply."""
    return FakeResponse(sample_csv("modis.csv"))


def test_timeout_is_sent(script, good):
    """Every request carries a timeout, 60 seconds by default."""
    script.replies = [good]
    nasa_wildfires.get_modis()
    assert script.kwargs["timeout"] == 60.0


def test_custom_timeout_is_sent(script, good):
    """A caller can choose the timeout."""
    script.replies = [good]
    nasa_wildfires.get_hotspots("modis", timeout=5)
    assert script.kwargs["timeout"] == 5


@pytest.mark.parametrize(
    "failure",
    [
        requests.ConnectionError("no route"),
        requests.Timeout("too slow"),
        FakeResponse(status_code=503),
        FakeResponse(status_code=502),
        FakeResponse(status_code=429),
    ],
)
def test_retries_then_succeeds(script, good, failure):
    """A network problem or a busy server is tried again."""
    script.replies = [failure, good]
    data = nasa_wildfires.get_modis()
    assert len(data["features"]) == 3
    assert len(script.urls) == 2


def test_alternates_between_domains(script, good):
    """After a failure the next try goes to the other NASA domain."""
    script.replies = [FakeResponse(status_code=500), good]
    nasa_wildfires.get_modis()
    domains = {url.split("/")[2] for url in script.urls}
    assert domains == set(fetch.DOMAINS)


def test_gives_up_with_a_clear_error(script):
    """After every try fails a NASAError says what happened last."""
    script.replies = [FakeResponse(status_code=503)] * 4
    with pytest.raises(NASAError, match="status 503") as caught:
        nasa_wildfires.get_modis()
    assert caught.value.status_code == 503
    assert caught.value.url is not None
    assert len(script.urls) == 4


def test_network_error_message(script):
    """A network failure that never clears is reported as unreachable."""
    script.replies = [requests.ConnectionError("down")] * 4
    with pytest.raises(NASAError, match="Could not reach NASA"):
        nasa_wildfires.get_modis()


def test_not_found_is_not_retried(script):
    """A 404 will not fix itself, so it fails on the first try."""
    script.replies = [FakeResponse(status_code=404)]
    with pytest.raises(NASAError, match="404"):
        nasa_wildfires.get_modis()
    assert len(script.urls) == 1


def test_error_is_not_an_assertion_error(script):
    """The old AssertionError is gone."""
    script.replies = [FakeResponse(status_code=404)]
    with pytest.raises(NASAError) as caught:
        nasa_wildfires.get_modis()
    assert not isinstance(caught.value, AssertionError)


def test_web_page_instead_of_csv(script):
    """A 200 reply that is not a hotspot file is a data error."""
    script.replies = [FakeResponse(b"<html>Maintenance</html>")]
    with pytest.raises(NASADataError, match="does not look like"):
        nasa_wildfires.get_modis()


def test_not_text(script):
    """Bytes that are not text are a data error."""
    script.replies = [FakeResponse(b"\xff\xfe\x00\x01")]
    with pytest.raises(NASADataError):
        nasa_wildfires.get_modis()


def test_bad_row_in_records(script, good):
    """A row that cannot be read raises a data error, which is a ValueError."""
    body = good.content.replace(b"327.18", b"hot")
    script.replies = [FakeResponse(body)]
    with pytest.raises(ValueError, match="Could not read"):
        nasa_wildfires.get_hotspot_records("modis")


def test_verbose_goes_to_stderr(script, good, capsys):
    """Progress messages stay out of standard output, so JSON stays valid."""
    script.replies = [good]
    nasa_wildfires.get_modis(verbose=True)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "Requesting https://" in captured.err


def test_cli_error_is_one_clean_line(script):
    """The command line prints one error line and exits with code 1."""
    script.replies = [FakeResponse(status_code=404)]
    result = CliRunner().invoke(cmd, ["modis"])
    assert result.exit_code == 1
    assert result.output.startswith("Error: NASA sent back status 404")
    assert "Traceback" not in result.output


def test_cli_timeout_option(script, good):
    """The --timeout option reaches the request."""
    script.replies = [good]
    result = CliRunner().invoke(cmd, ["modis", "--timeout", "7"])
    assert result.exit_code == 0
    assert script.kwargs["timeout"] == 7.0
