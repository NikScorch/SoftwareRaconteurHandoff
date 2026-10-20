from datetime import datetime

import pytest

import main
from analysis import ComparisonError, CountryActivity, compare_countries
from preparation import EvaRecord

RECORDS = [
    EvaRecord("USA", datetime(1989, 12, 31), 10.0),   # just before the period
    EvaRecord("USA", datetime(1990, 1, 1), 2.0),      # first day of start year
    EvaRecord("USA", datetime(1995, 6, 1), 4.0),
    EvaRecord("USA", None, 50.0),                     # undated: never in a period
    EvaRecord("Russia", datetime(1992, 3, 1), 3.0),
    EvaRecord("Russia", datetime(1995, 12, 31), 1.5),  # last day of end year
    EvaRecord("Russia", datetime(1996, 1, 1), 20.0),   # just after the period
]


def test_compare_countries_reports_count_total_average_and_leader():
    result = compare_countries(RECORDS, "USA", "Russia", 1990, 1995)

    assert result.first == CountryActivity("USA", 2, 6.0, 3.0)
    assert result.second == CountryActivity("Russia", 2, 4.5, 2.25)
    assert result.leader == "USA"


def test_compare_countries_includes_start_and_end_years():
    result = compare_countries(RECORDS, "USA", "Russia", 1989, 1996)

    assert result.first.eva_count == 3
    assert result.second.eva_count == 3
    assert result.leader == "Russia"


def test_country_without_evas_in_period_has_zero_and_no_average():
    result = compare_countries(RECORDS, "USA", "Russia", 1996, 2000)

    assert result.first == CountryActivity("USA", 0, 0.0, None)
    assert result.second == CountryActivity("Russia", 1, 20.0, 20.0)
    assert result.leader == "Russia"


def test_equal_totals_are_reported_as_a_tie():
    records = [EvaRecord("USA", datetime(2000, 1, 1), 2.5),
               EvaRecord("Russia", datetime(2000, 5, 1), 1.25),
               EvaRecord("Russia", datetime(2000, 9, 1), 1.25)]

    assert compare_countries(records, "USA", "Russia", 2000, 2000).leader is None


def test_period_with_no_evas_at_all_is_a_tie():
    result = compare_countries(RECORDS, "USA", "Russia", 2050, 2060)

    assert result.first.average_hours is None
    assert result.second.average_hours is None
    assert result.leader is None


def test_country_names_are_matched_ignoring_case():
    result = compare_countries(RECORDS, "usa", " RUSSIA ", 1990, 1995)

    assert (result.first.country, result.second.country) == ("USA", "Russia")


def test_start_year_after_end_year_is_rejected():
    with pytest.raises(ComparisonError, match="after end year"):
        compare_countries(RECORDS, "USA", "Russia", 2000, 1990)


def test_unknown_country_is_rejected():
    with pytest.raises(ComparisonError, match="unknown country 'Mars'"):
        compare_countries(RECORDS, "USA", "Mars", 1990, 1995)


@pytest.mark.parametrize("args, message", [
    (["compare", "USA", "Russia", "2000", "1990"], "after end year"),
    (["compare", "USA", "Mars", "1990", "2000"], "unknown country"),
])
def test_cli_reports_invalid_comparison_without_crashing(args, message, capsys):
    assert main.main(args) == 1
    assert message in capsys.readouterr().err


def test_cli_prints_comparison_for_bundled_data(capsys):
    assert main.main(["compare", "USA", "Russia", "1990", "1999"]) == 0

    # Expected values calculated independently from the raw JSON.
    out = capsys.readouterr().out
    rows = [line.split() for line in out.splitlines()]
    assert ["USA", "27", "173.52", "6.43"] in rows
    assert ["Russia", "57", "266.95", "4.68"] in rows
    assert "Russia has the greater total EVA duration" in out
