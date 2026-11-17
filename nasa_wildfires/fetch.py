"""Download NASA's hotspot CSV files, with a timeout and retries."""

from __future__ import annotations

import csv
import random
import sys
import time
from typing import Protocol

import requests

from .errors import NASADataError, NASAError

DOMAINS = (
    "firms.modaps.eosdis.nasa.gov",
    "firms2.modaps.eosdis.nasa.gov",
)
"""NASA's two copies of the same files. The second is a backup for the first."""

DEFAULT_TIMEOUT = 60.0
"""How many seconds to wait for NASA before giving up on one attempt."""

DEFAULT_TRIES = 4
"""How many times to try before raising an error."""

RETRY_STATUS_CODES = frozenset({408, 429})
"""Statuses worth another try. Every 5xx status is also worth another try."""


class Reply(Protocol):
    """What a request function must hand back: a status code and the file's bytes.

    A ``requests.Response`` fits this.
    """

    @property
    def status_code(self) -> int:
        """The web status, such as 200 or 404."""
        ...

    @property
    def content(self) -> bytes:
        """The body of the reply, as bytes."""
        ...


class Fetcher(Protocol):
    """A function that makes a web request for this package.

    Pass one as ``get`` to add retries, logging or custom headers. ``requests.get``
    fits this, and is the default.

    Examples:
        >>> import requests
        >>> fetcher: Fetcher = requests.get
    """

    def __call__(self, url: str, *, timeout: float) -> Reply:
        """Request a web address.

        Args:
            url: The address to request.
            timeout: The seconds to wait before giving up.

        Returns:
            The reply.
        """
        ...


def download_rows(
    csv_path: str,
    verbose: bool = False,
    timeout: float = DEFAULT_TIMEOUT,
    tries: int = DEFAULT_TRIES,
    get: Fetcher | None = None,
) -> list[dict[str, str]]:
    """Download one of NASA's hotspot CSV files and read its rows.

    A download is tried again when NASA cannot be reached, takes too long, or
    answers with a server error or "too many requests". The two NASA domains
    take turns, starting with a random one, so a problem with one is skipped by
    the next try. The wait before each new try doubles, starting at 2 seconds.
    Any other bad status, such as "not found", fails right away.

    Args:
        csv_path: The path of the file, relative to NASA's active fire data
            folder, such as "modis-c6.1/csv/MODIS_C6_1_Global_24h.csv".
        verbose: Print each request to standard error. Defaults to False.
        timeout: Seconds to wait for NASA on each try. Defaults to 60.
        tries: How many tries to make in all. Defaults to 4.
        get: A function that makes the web request, such as ``requests.get``
            (the default). It is called as ``get(url, timeout=seconds)`` and
            must return something with ``status_code`` and ``content``. Its
            ``requests`` errors are retried like the default's. Any other error
            it raises is passed on untouched.

    Returns:
        One dictionary of column names to text for each row. A file with only a
        header gives an empty list.

    Raises:
        NASAError: If every try fails, or NASA answers with a status that is
            not worth trying again.
        NASADataError: If the file arrives but is not a hotspot CSV.

    Examples:
        >>> rows = download_rows("modis-c6.1/csv/MODIS_C6_1_Alaska_24h.csv")
        >>> rows = download_rows(
        ...     "noaa-21-viirs-c2/csv/J2_VIIRS_C2_Global_7d.csv", timeout=120, tries=2
        ... )
        >>> rows = download_rows(
        ...     "modis-c6.1/csv/MODIS_C6_1_Alaska_24h.csv", get=my_get
        ... )
    """
    fetch: Fetcher = get or requests.get
    start = random.randrange(len(DOMAINS))
    problem = None
    for attempt in range(max(tries, 1)):
        if attempt:
            time.sleep(2**attempt + random.random())
        domain = DOMAINS[(start + attempt) % len(DOMAINS)]
        url = f"https://{domain}/data/active_fire/{csv_path}"
        if verbose:
            print(f"Requesting {url}", file=sys.stderr)
        try:
            response = fetch(url, timeout=timeout)
        except (requests.ConnectionError, requests.Timeout) as error:
            problem = NASAError(f"Could not reach NASA at {url}: {error}", url=url)
            continue
        except requests.RequestException as error:
            raise NASAError(f"Request to {url} failed: {error}", url=url) from error

        status = response.status_code
        if status >= 500 or status in RETRY_STATUS_CODES:
            problem = NASAError(
                f"NASA sent back status {status} for {url}", url=url, status_code=status
            )
            continue
        if status >= 400:
            raise NASAError(
                f"NASA sent back status {status} for {url}", url=url, status_code=status
            )
        return _read_rows(response.content, url)

    assert problem is not None
    raise problem


def _read_rows(content: bytes, url: str) -> list[dict[str, str]]:
    """Read the rows of a hotspot CSV that NASA sent back.

    Args:
        content: The bytes of the file.
        url: The address it came from, used in error messages.

    Returns:
        One dictionary of column names to text for each row.

    Raises:
        NASADataError: If the file is not UTF-8 text or does not have latitude
            and longitude columns.

    Examples:
        >>> _read_rows(b"latitude,longitude\\n1.5,2.5\\n", "https://example.com")
        [{'latitude': '1.5', 'longitude': '2.5'}]
    """
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise NASADataError(f"The file at {url} is not text", url=url) from error
    reader = csv.DictReader(text.splitlines(), delimiter=",")
    columns = reader.fieldnames or []
    if "latitude" not in columns or "longitude" not in columns:
        raise NASADataError(
            f"The file at {url} does not look like a hotspot CSV: "
            "it has no latitude and longitude columns",
            url=url,
        )
    return list(reader)
