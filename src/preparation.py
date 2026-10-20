"""Validating raw EVA data and preparing it for analysis.

This is the only module that knows the raw field names and the "H:MM"
duration format. Everything downstream works with EvaRecord.
"""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class EvaRecord:
    country: str | None
    date: datetime | None
    duration_hours: float


def parse_duration(text):
    """Convert an "H:MM" duration string into hours.

    Raises ValueError if the text is not a valid duration.
    """
    hours, minutes = map(int, text.split(":"))
    if hours < 0 or not 0 <= minutes < 60:
        raise ValueError(f"invalid duration: {text!r}")
    return hours + minutes / 60


def parse_date(text):
    """Return the ISO 8601 date in ``text``, or None if it is missing or invalid."""
    if not text:
        return None
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def prepare_records(raw_evas):
    """Convert raw EVA dictionaries into EvaRecords.

    EVAs without a valid duration are dropped. EVAs without a valid date are
    kept with ``date=None``: they still count towards per-country totals but
    cannot be placed on a timeline.
    """
    records = []
    for eva in raw_evas:
        duration_text = eva.get("duration")
        if not duration_text:
            continue
        try:
            duration_hours = parse_duration(duration_text)
        except ValueError:
            continue
        records.append(EvaRecord(
            country=eva.get("country"),
            date=parse_date(eva.get("date")),
            duration_hours=duration_hours,
        ))
    return records
