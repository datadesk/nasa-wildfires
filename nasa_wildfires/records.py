"""Typed records for the hotspots NASA publishes."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from .options import Satellite

PLATFORM_NAMES = {
    "T": "Terra",
    "A": "Aqua",
    "N": "Suomi-NPP",
    "N20": "NOAA-20",
    "N21": "NOAA-21",
}
"""The satellite names that go with the short codes in NASA's ``satellite`` column."""


@dataclass(frozen=True, slots=True)
class Hotspot:
    """One heat spot seen by a satellite.

    A hotspot is not a confirmed wildfire. It is a patch of ground, roughly
    375 meters to 1 kilometer wide, that looked hot to the satellite. Fires set
    on purpose, industrial flares and gas burning show up too.

    The MODIS and VIIRS instruments report slightly different columns. The two
    brightness fields hold the matching values from either one, and the two
    confidence fields are filled in one at a time.

    Attributes:
        latitude: Degrees north of the equator, negative in the south.
        longitude: Degrees east of the prime meridian, negative in the west.
        acquired_at: When the satellite saw the spot, in UTC.
        satellite: The instrument family that was asked for.
        platform: The name of the satellite itself, such as "Terra" or
            "NOAA-21". Unknown codes are kept as NASA wrote them.
        brightness: How hot the spot looked, in kelvin. This is NASA's
            ``brightness`` column for MODIS and ``bright_ti4`` for VIIRS.
        brightness_2: A second brightness reading from a longer wavelength, in
            kelvin. This is NASA's ``bright_t31`` column for MODIS and
            ``bright_ti5`` for VIIRS.
        scan: The width of the pixel across the satellite's path, in
            kilometers.
        track: The height of the pixel along the satellite's path, in
            kilometers.
        frp: Fire radiative power, the heat the fire gives off, in megawatts.
        is_daytime: True if the satellite passed over in daylight.
        version: NASA's processing version, such as "6.1NRT". NRT means near
            real time, so the numbers can be refined later.
        confidence_percent: How sure NASA is that this is a real hot spot, from
            0 to 100. Filled in for MODIS, otherwise None.
        confidence_level: "low", "nominal" or "high". Filled in for VIIRS,
            otherwise None.

    Examples:
        >>> row = {
        ...     "latitude": "19.40542",
        ...     "longitude": "-155.29007",
        ...     "bright_ti4": "344.71",
        ...     "scan": "0.55",
        ...     "track": "0.51",
        ...     "acq_date": "2026-11-16",
        ...     "acq_time": "0005",
        ...     "satellite": "N21",
        ...     "confidence": "nominal",
        ...     "version": "2.0NRT",
        ...     "bright_ti5": "301.87",
        ...     "frp": "18.51",
        ...     "daynight": "D",
        ... }
        >>> hotspot = Hotspot.from_row(row, Satellite.VIIRS_NOAA21)
        >>> hotspot.acquired_at.isoformat()
        '2026-11-16T00:05:00+00:00'
        >>> hotspot.platform
        'NOAA-21'
    """

    latitude: float
    longitude: float
    acquired_at: datetime
    satellite: Satellite
    platform: str
    brightness: float
    brightness_2: float
    scan: float
    track: float
    frp: float
    is_daytime: bool
    version: str
    confidence_percent: int | None = None
    confidence_level: str | None = None

    @classmethod
    def from_row(cls, row: dict[str, str], satellite: Satellite) -> Hotspot:
        """Build a hotspot from one row of NASA's CSV.

        Args:
            row: The row as a dictionary of column names to text, such as
                ``csv.DictReader`` produces.
            satellite: The instrument family the row was downloaded for. It
                decides which brightness columns to read.

        Returns:
            The hotspot, with numbers parsed and the date and time combined
            into one UTC ``acquired_at``.

        Raises:
            ValueError: If a column is missing or a value cannot be read.

        Examples:
            >>> row = {
            ...     "latitude": "-14.51802",
            ...     "longitude": "127.9279",
            ...     "brightness": "327.18",
            ...     "scan": "1.09",
            ...     "track": "1.04",
            ...     "acq_date": "2026-11-16",
            ...     "acq_time": "0000",
            ...     "satellite": "T",
            ...     "confidence": "0",
            ...     "version": "6.1NRT",
            ...     "bright_t31": "300.26",
            ...     "frp": "19.15",
            ...     "daynight": "D",
            ... }
            >>> hotspot = Hotspot.from_row(row, Satellite.MODIS)
            >>> hotspot.confidence_percent
            0
            >>> hotspot.confidence_level is None
            True
        """
        if satellite == Satellite.MODIS:
            hot_column, cool_column = "brightness", "bright_t31"
        else:
            hot_column, cool_column = "bright_ti4", "bright_ti5"
        try:
            acquired_at = _parse_time(row["acq_date"], row["acq_time"])
            confidence = row["confidence"].strip()
            code = row["satellite"].strip()
            daynight = row["daynight"].strip().upper()
            if daynight not in ("D", "N"):
                raise ValueError(f"daynight should be D or N, not {daynight!r}")
            return cls(
                latitude=float(row["latitude"]),
                longitude=float(row["longitude"]),
                acquired_at=acquired_at,
                satellite=satellite,
                platform=PLATFORM_NAMES.get(code, code),
                brightness=float(row[hot_column]),
                brightness_2=float(row[cool_column]),
                scan=float(row["scan"]),
                track=float(row["track"]),
                frp=float(row["frp"]),
                is_daytime=daynight == "D",
                version=row["version"].strip(),
                confidence_percent=int(confidence) if confidence.isdigit() else None,
                confidence_level=None if confidence.isdigit() else confidence.lower(),
            )
        except KeyError as error:
            raise ValueError(f"NASA's row has no {error} column") from error
        except ValueError as error:
            raise ValueError(f"Could not read NASA's row: {error}") from error


def _parse_time(acq_date: str, acq_time: str) -> datetime:
    """Combine NASA's date and time columns into one UTC time.

    Args:
        acq_date: The date as ``YYYY-MM-DD``.
        acq_time: The time of day as ``HHMM`` in UTC, which may drop leading
            zeros.

    Returns:
        A timezone-aware datetime in UTC.

    Examples:
        >>> _parse_time("2026-11-16", "0047").isoformat()
        '2026-11-16T00:47:00+00:00'
        >>> _parse_time("2026-11-16", "47").isoformat()
        '2026-11-16T00:47:00+00:00'
    """
    stamp = datetime.strptime(
        f"{acq_date} {acq_time.strip().zfill(4)}", "%Y-%m-%d %H%M"
    )
    return stamp.replace(tzinfo=UTC)
