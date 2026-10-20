"""Entry point: coordinates loading, preparation, analysis and presentation."""
import argparse
import sys
from pathlib import Path

import analysis
import presentation
from data_loader import load_eva_data
from preparation import prepare_records

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_DIR / "data" / "eva-data.json"
OUTPUT_DIR = PROJECT_DIR / "outputs"

CUMULATIVE_CHART = OUTPUT_DIR / "cumulative_duration.png"
COUNTRY_CHART = OUTPUT_DIR / "duration_per_country.png"
COUNTRY_CSV = OUTPUT_DIR / "duration_per_country.csv"


def run_reports(records, show):
    """Produce the cumulative-duration and duration-per-country reports."""
    OUTPUT_DIR.mkdir(exist_ok=True)

    dates, cumulative_hours = analysis.cumulative_duration(records)
    presentation.plot_cumulative_duration(dates, cumulative_hours, CUMULATIVE_CHART)

    country_totals = analysis.duration_per_country(records)
    presentation.print_country_totals(country_totals)
    presentation.plot_country_totals(country_totals, COUNTRY_CHART)
    presentation.save_country_totals_csv(country_totals, COUNTRY_CSV)

    if show:
        presentation.show_charts()


def run_comparison(records, args):
    """Compare two countries and print the result; return the exit status."""
    try:
        comparison = analysis.compare_countries(
            records, args.country_a, args.country_b, args.start_year, args.end_year)
    except analysis.ComparisonError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    presentation.print_comparison(comparison)
    return 0


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Process NASA EVA data.")
    parser.add_argument("--no-show", action="store_true",
                        help="save charts without opening a window")
    commands = parser.add_subparsers(dest="command")
    commands.add_parser("reports", help="generate the standard reports (default)")
    compare = commands.add_parser(
        "compare", help="compare EVA activity of two countries over a period of years")
    compare.add_argument("country_a")
    compare.add_argument("country_b")
    compare.add_argument("start_year", type=int)
    compare.add_argument("end_year", type=int)
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    try:
        raw_evas = load_eva_data(DATA_FILE)
    except (OSError, ValueError) as error:
        print(f"Could not read EVA data from {DATA_FILE}: {error}", file=sys.stderr)
        return 1
    records = prepare_records(raw_evas)
    if args.command == "compare":
        return run_comparison(records, args)
    run_reports(records, show=not args.no_show)
    return 0


if __name__ == "__main__":
    sys.exit(main())
