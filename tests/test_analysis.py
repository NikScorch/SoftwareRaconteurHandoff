import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pytest

from analysis import cumulative_duration, duration_per_country
from data_loader import load_eva_data
from preparation import EvaRecord, prepare_records

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "eva-data.json"


def test_cumulative_duration_sorts_by_date_and_skips_undated():
    records = [
        EvaRecord("USA", datetime(1970, 1, 1), 2.0),
        EvaRecord("Russia", None, 100.0),
        EvaRecord("Russia", datetime(1965, 3, 18), 0.5),
        EvaRecord("USA", datetime(1980, 6, 1), 1.5),
    ]

    dates, cumulative = cumulative_duration(records)

    assert dates == [datetime(1965, 3, 18), datetime(1970, 1, 1), datetime(1980, 6, 1)]
    assert cumulative == [0.5, 2.5, 4.0]


def test_cumulative_duration_of_no_records_is_empty():
    assert cumulative_duration([]) == ([], [])


def test_duration_per_country_includes_undated_records():
    records = [
        EvaRecord("USA", datetime(1970, 1, 1), 2.0),
        EvaRecord("USA", None, 1.5),
        EvaRecord("Russia", datetime(1990, 1, 1), 4.25),
    ]

    assert duration_per_country(records) == {"USA": 3.5, "Russia": 4.25}


def test_bundled_data_matches_pre_restructuring_output():
    # Values printed by the inherited data_handler.py before restructuring.
    totals = duration_per_country(prepare_records(load_eva_data(DATA_FILE)))

    assert totals == {"Russia": pytest.approx(626.58, abs=0.005),
                      "USA": pytest.approx(1360.07, abs=0.005)}


def test_analysis_does_not_depend_on_presentation():
    # Analysis must be usable without the plotting library being imported.
    src = Path(__file__).resolve().parent.parent / "src"
    code = "import sys, analysis; assert 'matplotlib' not in sys.modules"
    subprocess.run([sys.executable, "-c", code], cwd=src, check=True)
