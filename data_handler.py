import json
from datetime import datetime
import matplotlib.pyplot as plt
import csv

with open("eva-data.json", "r", encoding="utf-8") as file:
    eva_data = json.load(file)

records = []

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

dates = []
cumulative_hours = []
total_hours = 0

for date, duration_hours in records:
    total_hours += duration_hours
    dates.append(date)
    cumulative_hours.append(total_hours)

plt.plot(dates, cumulative_hours)
plt.xlabel("Year")
plt.ylabel("Cumulative EVA duration (hours)")
plt.tight_layout()
plt.savefig("cumulative_duration.png")
plt.show()

# new code..

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

country_totals = get_eva_duration_per_country(eva_data)

print("Total EVA hours per country:")
for country, country_hours in sorted(country_totals.items()):
    print(f"  {country}: {country_hours:.2f}")

def plot_country_totals(country_totals, output_path):
    plt.figure()
    plt.bar(list(country_totals.keys()), list(country_totals.values()))
    plt.xlabel("Country")
    plt.ylabel("Total EVA duration (hours)")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.show()

plot_country_totals(country_totals, "duration_per_country.png")

def save_country_totals_to_csv(country_totals, output_path):
    with open(output_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["country", "total_hours"])
        for country, country_hours in sorted(country_totals.items()):
            writer.writerow([country, f"{country_hours:.2f}"])

save_country_totals_to_csv(country_totals, "duration_per_country.csv")
print("\nSaved country totals to duration_per_country.csv")