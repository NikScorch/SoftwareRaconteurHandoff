## Eva-Proccesser Raconteur

A processor for NASA EVA data for module CS6514

It produces two reports from `data/eva-data.json`:

- **Cumulative EVA duration over time**, saved as `outputs/cumulative_duration.png`.
- **Total EVA duration per country**, printed to the console and saved as
  `outputs/duration_per_country.png` and `outputs/duration_per_country.csv`.

It also compares EVA activity between two countries over a range of years.

### Setup

Requires Python 3.10+.

```sh
python3 -m venv .venv
source .venv/bin/activate        # fish: source .venv/bin/activate.fish
pip install -r requirements.txt
```

### Running

```sh
python src/main.py                         # standard reports, opens the charts
python src/main.py --no-show               # standard reports, files only
python src/main.py compare USA Russia 1990 1999
```

Example comparison output:

```
EVA activity 1990-1999
  Country      EVAs  Total (h)  Average (h)
  USA            27     173.52         6.43
  Russia         57     266.95         4.68
Result: Russia has the greater total EVA duration.
```

- Both the start and end years are included.
- Country names are matched case-insensitively.
- A country with no EVAs in the period shows `0`, `0.00` and `unavailable`.
- Equal totals are reported as a tie.
- If the start year is after the end year, or the country is unknown, an
  error is printed and the exit code is 1.
- EVAs with no date in the dataset (44 of 375) can't be placed in a year, so
  they're excluded from comparisons. They still count in the per-country
  report. See ADR-002.

### Running the tests

```sh
python -m pytest
```

### Module structure

```
src/
  main.py          coordination: paths, command line, calls the layers below in order
  data_loader.py   reading data: loads the JSON file
  preparation.py   validating & preparing: raw dicts -> EvaRecord (parses "H:MM")
  analysis.py      calculations: cumulative duration, per-country totals, country comparison
  presentation.py  presenting results: charts, CSV, console output (only matplotlib user)
tests/             pytest tests for preparation, analysis and the comparison
data/              input data
outputs/           generated reports
docs/
  architecture.md  initial assessment, module diagram, maintainability evaluation
  adr/             architectural decision records
```

Data flows `data_loader → preparation → analysis → presentation`, with
`main.py` doing the coordination. Analysis functions are pure (no file access,
printing or plotting), so they can be tested with in-memory `EvaRecord`s.

### Architectural decision records

- [ADR-001: Split the single script into layered, single-responsibility modules](docs/adr/ADR-001-layered-module-structure.md)
- [ADR-002: Country comparison as a pure analysis function with a typed result and domain errors](docs/adr/ADR-002-country-comparison-as-pure-analysis.md)
