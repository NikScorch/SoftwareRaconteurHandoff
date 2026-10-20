# ADR-002: Implement the country comparison as a pure analysis function with a typed result and domain errors

**Status:** Accepted

## Context

The new functional requirement, *Compare EVA Activity Between Countries*,
asks for EVA count, total hours and average hours for two countries over an
inclusive range of years, plus the country with the greater total or a tie.
Invalid year ranges and unknown countries must be handled without the program
terminating unexpectedly.

Decisions needed:

1. Where the calculation lives and how it reuses existing analysis.
2. How results are passed to presentation, including "average unavailable" and
   "tie".
3. How invalid input is reported.
4. How records without a date are treated (44 of 375 EVAs, including Alexei
   Leonov's first EVA in 1965).

## Alternatives

**Calculation placement**

- A. Calculate and print in `main.py`. This is quick, but it mixes
  coordination with analysis and can't be tested without capturing stdout.
- B. A new `comparison.py` module. It's cohesive, but it would duplicate the
  aggregation that already exists in `analysis.py`.
- C. **Add `compare_countries()` to `analysis.py`**, built from
  `records_in_years()` plus the existing `duration_per_country()`.

**Result representation**

- A plain `dict`. It's flexible, but keys are untyped and easy to misspell.
- A pre-formatted string. This couples analysis to presentation, which breaks
  AR3.
- **Frozen dataclasses** `CountryActivity` and `CountryComparison`, with
  `average_hours=None` meaning unavailable and `leader=None` meaning a tie.

**Invalid input**

- Print an error inside the analysis function. That couples analysis to the
  console.
- Return `None` or an error code. Callers can silently ignore it.
- Treat an unknown country as "zero EVAs". It never fails, but a typo such as
  `Rusia` would quietly report zero instead of telling the user.
- **Raise `ComparisonError` (a `ValueError`) from analysis and catch it in
  `main.py`**, which prints a message and returns exit code 1.

## Decision

- `analysis.compare_countries(records, country_a, country_b, start_year,
  end_year)` returns a `CountryComparison`. It filters with
  `records_in_years()` (inclusive), then **reuses `duration_per_country()`**
  for totals, adding a small `eva_count_per_country()` for counts.
- An inverted year range or a country not present in the data raises
  `ComparisonError`. Country names match case-insensitively, and the error
  lists the known countries.
- A known country with no EVAs in the period reports count 0, total 0.00 and
  average `None`, which presentation shows as "unavailable".
- Equal totals (compared with `math.isclose`) give `leader=None`, which
  presentation shows as a tie.
- `presentation.print_comparison()` formats the result, and `main.py` adds a
  `compare` subcommand. Non-integer years are rejected by `argparse` with a
  usage message.
- **Undated EVAs are excluded** from comparisons because they can't be placed
  in a year.

## Rationale

- The layered structure from ADR-001 meant the feature fitted into existing
  responsibilities. Only `analysis`, `presentation` and `main` changed;
  `data_loader` and `preparation` were not modified (`git show --stat
  f749f10`).
- Reusing `duration_per_country()` keeps a single definition of "total EVA
  duration".
- A typed result keeps analysis independent of output format. The same
  `CountryComparison` could feed a chart or CSV later without recalculating.
- Raising a domain exception keeps the rules in one testable place, while the
  coordinator decides how to report them. The rules are tested directly in
  `tests/test_comparison.py`.

## Consequences

**Benefits**

- Every rule in the requirement (inclusive years, zero/unavailable, tie,
  invalid range, unknown country) is covered by an automated test with known
  inputs.
- New output formats for the comparison need only presentation changes.

**Limitations and trade-offs**

- Excluding undated EVAs means comparison totals over the full date range
  (1965–2013: USA 1257.13 h, Russia 527.90 h) are lower than the
  all-time per-country totals (USA 1360.07 h, Russia 626.58 h). This is a
  data-quality limitation; it's documented here and in the README.
- "Unknown country" means "not present in the dataset", so the set of valid
  countries changes if the data changes.
- Comparing a country with itself is allowed and reports a tie. It wasn't
  worth an extra rule.
