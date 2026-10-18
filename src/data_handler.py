import json
from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt
import csv

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_DIR / "data" / "eva-data.json"
OUTPUT_DIR = PROJECT_DIR / "outputs"

CUMULATIVE_CHART = OUTPUT_DIR / "cumulative_duration.png"
COUNTRY_CHART = OUTPUT_DIR / "duration_per_country.png"
COUNTRY_CSV = OUTPUT_DIR / "duration_per_country.csv"

OUTPUT_DIR.mkdir(exist_ok=True)

records = []
dates = []
cumulative_hours = []
total_hours = 0

def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        eva_data = json.load(file)
    return eva_data

eva_data = load_json(DATA_FILE)

for eva in eva_data:
    date_text = eva.get("date")
    duration_text = eva.get("duration")
    if not date_text or not duration_text:
        continue
    date = datetime.fromisoformat(date_text)
    hours, minutes = map(int, duration_text.split(":"))
    duration_hours = hours + minutes / 60
    records.append((date, duration_hours))

records.sort(key=lambda record: record[0])

for date, duration_hours in records:
    total_hours += duration_hours
    dates.append(date)
    cumulative_hours.append(total_hours)

plt.plot(dates, cumulative_hours)
plt.xlabel("Year")
plt.ylabel("Cumulative EVA duration (hours)")
plt.tight_layout()
plt.savefig(CUMULATIVE_CHART)
plt.show()

def get_eva_duration_per_country(eva_data):
    totals = {}
    for eva in eva_data:
        duration_text = eva.get("duration")
        if not duration_text:
            continue
        country = eva.get("country")
        hours, minutes = map(int, duration_text.split(":"))
        totals[country] = totals.get(country, 0) + hours + minutes / 60
    return totals

def plot_country_totals(country_totals, output_path):
    plt.figure()
    plt.bar(list(country_totals.keys()), list(country_totals.values()))
    plt.xlabel("Country")
    plt.ylabel("Total EVA duration (hours)")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.show()

def save_country_totals_to_csv(country_totals, output_path):
    with open(output_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["country", "total_hours"])
        for country, country_hours in sorted(country_totals.items()):
            writer.writerow([country, f"{country_hours:.2f}"])

country_totals = get_eva_duration_per_country(eva_data)
for country, country_hours in sorted(country_totals.items()):
    print(f"  {country}: {country_hours:.2f}")
plot_country_totals(country_totals, COUNTRY_CHART)
save_country_totals_to_csv(country_totals, COUNTRY_CSV)