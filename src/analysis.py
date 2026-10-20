"""Calculations over prepared EVA records.

Functions here are pure: they take EvaRecords and return plain values, and
never read files, print or plot.
"""


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
