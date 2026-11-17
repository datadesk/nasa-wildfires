"""Shared test setup that keeps the tests off NASA's real website."""

from pathlib import Path

import pytest

DATA = Path(__file__).parent / "data"


class FakeResponse:
    """A stand-in for a ``requests`` response."""

    def __init__(self, content: bytes = b"", status_code: int = 200) -> None:
        self.content = content
        self.status_code = status_code
        self.ok = status_code < 400


@pytest.fixture(autouse=True)
def no_waiting(monkeypatch):
    """Skip the pauses between retries so the tests run fast."""
    from nasa_wildfires import fetch

    monkeypatch.setattr(fetch.time, "sleep", lambda seconds: None)


@pytest.fixture
def sample_csv():
    """Return a function that reads a saved CSV sample as bytes."""

    def read(name: str) -> bytes:
        return (DATA / name).read_bytes()

    return read


@pytest.fixture
def fake_nasa(monkeypatch, sample_csv):
    """Replace ``requests.get`` and record the addresses that were asked for.

    The fake answers every request with the sample whose name is in
    ``fake_nasa.sample``. Set it before calling the package.
    """
    from nasa_wildfires import fetch

    class Fake:
        sample = "modis.csv"
        urls: list[str]

    fake = Fake()
    fake.urls = []

    def get(url, *args, **kwargs):
        fake.urls.append(url)
        fake.kwargs = kwargs
        return FakeResponse(sample_csv(fake.sample))

    monkeypatch.setattr(fetch.requests, "get", get)
    return fake
