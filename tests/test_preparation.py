from datetime import datetime

import pytest

from preparation import EvaRecord, parse_duration, prepare_records


def test_parse_duration_converts_hours_and_minutes():
    assert parse_duration("0:36") == pytest.approx(0.6)
    assert parse_duration("7:45") == pytest.approx(7.75)
    assert parse_duration("0:00") == 0


@pytest.mark.parametrize("text", ["abc", "5", "1:2:3", "1:60", "-1:30", "1:-5"])
def test_parse_duration_rejects_invalid_text(text):
    with pytest.raises(ValueError):
        parse_duration(text)


def test_prepare_records_keeps_undated_and_drops_invalid_durations():
    raw = [
        {"country": "USA", "date": "1965-06-03T00:00:00.000", "duration": "0:36"},
        {"country": "USA", "duration": "1:30"},                        # no date: kept
        {"country": "Russia", "date": "not a date", "duration": "2:00"},  # bad date: kept
        {"country": "USA", "date": "1973-05-25T00:00:00.000"},        # no duration: dropped
        {"country": "USA", "date": "1973-05-26T00:00:00.000", "duration": "x"},  # dropped
    ]

    assert prepare_records(raw) == [
        EvaRecord("USA", datetime(1965, 6, 3), pytest.approx(0.6)),
        EvaRecord("USA", None, 1.5),
        EvaRecord("Russia", None, 2.0),
    ]
