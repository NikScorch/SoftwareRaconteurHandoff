"""Calculations over prepared EVA records.

Functions here are pure: they take EvaRecords and return plain values, and
never read files, print or plot.
"""
import math
from dataclasses import dataclass


def cumulative_duration(records):
    """Return (dates, cumulative_hours) for dated EVAs in chronological order."""
    dated = sorted((r for r in records if r.date is not None), key=lambda r: r.date)
    dates = []
    cumulative_hours = []
    total_hours = 0
    for record in dated:
        total_hours += record.duration_hours
        dates.append(record.date)
        cumulative_hours.append(total_hours)
    return dates, cumulative_hours


def duration_per_country(records):
    """Return a mapping of country to total EVA duration in hours."""
    totals = {}
    for record in records:
        totals[record.country] = totals.get(record.country, 0) + record.duration_hours
    return totals


@dataclass(frozen=True)
class CountryActivity:
    country: str
    eva_count: int
    total_hours: float
    average_hours: float | None  # None when the country has no EVAs in the period


@dataclass(frozen=True)
class CountryComparison:
    start_year: int
    end_year: int
    first: CountryActivity
    second: CountryActivity
    leader: str | None  # country with the greater total duration; None for a tie


class ComparisonError(ValueError):
    """Raised when a comparison is requested with invalid parameters."""


def records_in_years(records, start_year, end_year):
    """Return dated records whose year is between start_year and end_year inclusive."""
    return [r for r in records
            if r.date is not None and start_year <= r.date.year <= end_year]


def eva_count_per_country(records):
    """Return a mapping of country to number of EVAs."""
    counts = {}
    for record in records:
        counts[record.country] = counts.get(record.country, 0) + 1
    return counts


def resolve_country(records, name):
    """Return the country name used in ``records`` that matches ``name``, ignoring case.

    Raises ComparisonError if no record has that country.
    """
    known = sorted({r.country for r in records if r.country})
    for country in known:
        if country.casefold() == name.strip().casefold():
            return country
    raise ComparisonError(
        f"unknown country {name!r}; known countries: {', '.join(known)}")


def compare_countries(records, country_a, country_b, start_year, end_year):
    """Compare EVA activity of two countries between two years, inclusive.

    Raises ComparisonError for an invalid year range or an unknown country.
    """
    if start_year > end_year:
        raise ComparisonError(
            f"start year {start_year} is after end year {end_year}")
    country_a = resolve_country(records, country_a)
    country_b = resolve_country(records, country_b)

    in_period = records_in_years(records, start_year, end_year)
    totals = duration_per_country(in_period)
    counts = eva_count_per_country(in_period)

    def activity(country):
        count = counts.get(country, 0)
        total = totals.get(country, 0.0)
        return CountryActivity(country, count, total, total / count if count else None)

    first, second = activity(country_a), activity(country_b)
    if math.isclose(first.total_hours, second.total_hours, abs_tol=1e-9):
        leader = None
    elif first.total_hours > second.total_hours:
        leader = first.country
    else:
        leader = second.country
    return CountryComparison(start_year, end_year, first, second, leader)
