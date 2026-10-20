"""Presenting analysis results as charts, CSV files and console output.

This is the only module that depends on matplotlib.
"""
import csv

import matplotlib.pyplot as plt


def plot_cumulative_duration(dates, cumulative_hours, output_path):
    plt.figure()
    plt.plot(dates, cumulative_hours)
    plt.xlabel("Year")
    plt.ylabel("Cumulative EVA duration (hours)")
    plt.tight_layout()
    plt.savefig(output_path)


def plot_country_totals(country_totals, output_path):
    plt.figure()
    plt.bar(list(country_totals.keys()), list(country_totals.values()))
    plt.xlabel("Country")
    plt.ylabel("Total EVA duration (hours)")
    plt.tight_layout()
    plt.savefig(output_path)


def save_country_totals_csv(country_totals, output_path):
    with open(output_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["country", "total_hours"])
        for country, country_hours in sorted(country_totals.items()):
            writer.writerow([country, f"{country_hours:.2f}"])


def print_country_totals(country_totals):
    for country, country_hours in sorted(country_totals.items()):
        print(f"  {country}: {country_hours:.2f}")


def show_charts():
    """Display every chart created so far."""
    plt.show()
