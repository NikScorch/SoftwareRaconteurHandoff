# ADR-001: Split the single script into layered, single-responsibility modules

**Status:** Accepted

## Context

The inherited application is one script, `src/data_handler.py`, that reads the
JSON file, parses dates and durations, calculates the results, draws charts,
writes a CSV and coordinates the run. All of this happens at import time.

This causes concrete problems:

- The duration parsing is duplicated (lines 35 and 60).
- The calculations read raw JSON keys and parse strings themselves, so a
  change to the data format affects every calculation.
- No calculation can be tested without reading the real data file, writing
  output files and opening matplotlib windows.
- The upcoming country-comparison requirement needs the same parsing and
  aggregation again. Adding it to the script would mean a third copy of the
  parsing and more global state.

AR1, AR2, AR3 and AR4 require the responsibilities to be separated into
cohesive modules with low coupling.

## Alternatives

1. **Keep one file and wrap the top-level code in functions.** This makes the
   code importable but leaves every responsibility in one unit, so it fails
   AR1 and AR2. Coupling between parsing and analysis stays.
2. **Split by feature** (`cumulative.py`, `country_totals.py`, each doing its
   own load, parse, calculate and plot). Each file would be cohesive around a
   report but still mix every layer. Parsing would be duplicated in each
   feature, or need a shared module anyway.
3. **Split by responsibility into a layered pipeline**: `data_loader` →
   `preparation` → `analysis` → `presentation`, coordinated by `main`, with a
   typed `EvaRecord` passed between preparation and analysis.
4. **Class-based design** (e.g. an `EvaRepository`, `Analyzer` and `Reporter`
   with abstract base classes). This would separate concerns, but it's more
   abstraction than a ~100-line program needs, which the brief warns against.

## Decision

Adopt **alternative 3**. Create five modules in `src/`, each owning one AR1
responsibility:

| Module | Owns |
|--------|------|
| `data_loader.py` | Reading data |
| `preparation.py` | Validating and preparing data (`EvaRecord`, `parse_duration`, `prepare_records`) |
| `analysis.py` | Calculations and analysis (pure functions) |
| `presentation.py` | Presenting results (charts, CSV, console) |
| `main.py` | Coordinating execution (paths, CLI, call order) |

Modules communicate through plain functions and a small frozen dataclass,
`EvaRecord(country, date, duration_hours)`. `src/data_handler.py` is replaced
by `main.py` as the entry point.

## Rationale

- **Boundaries follow the AR1 responsibilities**, so each module has one
  reason to change. A data format change touches `data_loader` and
  `preparation`; a new chart touches `presentation`; a new statistic touches
  `analysis`.
- **`EvaRecord` breaks the coupling between analysis and the raw format.**
  Field names and the `"H:MM"` format are known only to `preparation`. The
  duplicated parsing becomes a single `parse_duration` function.
- **Analysis is pure**, with no file access, printing or matplotlib. It can be
  tested with hand-built `EvaRecord`s (AR6).
- **Functions plus one dataclass** are the smallest structure that meets the
  requirements. No framework or new third-party dependency is introduced.

## Consequences

**Benefits**

- Each module can be read, changed and tested on its own.
- New analyses can be added to `analysis.py` and wired up in `main.py` without
  touching the loader or the parsing.
- Importing any module no longer has side effects.

**Limitations and trade-offs**

- Five files instead of one. A reader has to follow the call order in
  `main.py` to see the whole flow.
- The run is no longer one top-to-bottom script, which was arguably easier to
  read for a beginner.
- Small behaviour change: both charts now open together at the end of the run
  instead of one after the other. A `--no-show` flag was added so the reports
  can be generated without opening windows. Numeric outputs are unchanged.
- Records whose duration or date can't be parsed are now handled by
  `preparation` instead of crashing the program. A bad duration drops the
  record; a bad date is treated as a missing date. The bundled data has no
  such records, so the outputs are identical.
