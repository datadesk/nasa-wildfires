"""Shared test setup that keeps the tests off NASA's real website."""

from pathlib import Path

import pytest

DATA = Path(__file__).parent / "data"


class FakeResponse:
    """A stand-in for a ``requests`` response."""

    def __init__(self, content: bytes, status_code: int = 200) -> None:
        self.content = content
        self.status_code = status_code
        self.ok = status_code < 400


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
    import nasa_wildfires

    class Fake:
        sample = "modis.csv"
        urls: list[str]

    fake = Fake()
    fake.urls = []

    def get(url, *args, **kwargs):
        fake.urls.append(url)
        return FakeResponse(sample_csv(fake.sample))

    monkeypatch.setattr(nasa_wildfires.requests, "get", get)
    return fake
