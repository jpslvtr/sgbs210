import os
import re
from datetime import datetime

def extract_mse_over_time(file_content):
    mse_pattern = re.compile(r"Time Step \d+: MSE = ([\d.e-]+)")
    return [float(mse) for mse in mse_pattern.findall(file_content)]

def extract_day_of_week(file_content):
    arrival_time_pattern = re.compile(r"Arrival Time: (\d{4}-\d{2}-\d{2}) \d{2}:\d{2}:\d{2}")
    days_of_week = []
    for match in arrival_time_pattern.findall(file_content):
        arrival_date = datetime.strptime(match, "%Y-%m-%d")
        days_of_week.append(arrival_date.weekday())
    return days_of_week


def analyze_files(folder_path):
    ship_quality = {}
    day_quality = {i: [] for i in range(7)}
    journey_count_quality = {}

    for filename in os.listdir(folder_path):
        if filename.endswith("_4.txt"):
            with open(os.path.join(folder_path, filename), 'r') as file:
                content = file.read()
                mse_over_time = extract_mse_over_time(content)
                days_of_week = extract_day_of_week(content)
                journey_count = content.count("Arrival Time:")

                if mse_over_time:
                    quality = mse_over_time[-1] - mse_over_time[0]  # Change here

                    ship_id = filename.split('_')[0]
                    ship_quality[ship_id] = quality

                    for day in days_of_week:
                        day_quality[day].append(quality)

                    if journey_count not in journey_count_quality:
                        journey_count_quality[journey_count] = []
                    journey_count_quality[journey_count].append(quality)

    sorted_ship_quality = dict(sorted(ship_quality.items(), key=lambda item: item[1], reverse=True))

    # Average quality for each day of the week
    for day, qualities in day_quality.items():
        if qualities:
            day_quality[day] = sum(qualities) / len(qualities)
        else:
            day_quality[day] = 0

    # Rank days by quality
    ranked_days = sorted(day_quality.items(), key=lambda x: x[1], reverse=True)

    for count, qualities in journey_count_quality.items():
        if qualities:
            journey_count_quality[count] = sum(qualities) / len(qualities)
        else:
            journey_count_quality[count] = 0
    sorted_journey_count_quality = dict(sorted(journey_count_quality.items(), key=lambda item: item[1], reverse=True))

    return sorted_ship_quality, ranked_days, sorted_journey_count_quality

folder_path = '../data_james/4_results'
ranked_ships, ranked_days, sorted_journey_count_quality = analyze_files(folder_path)

print("Ranked Ships by Quality of Prediction:")
for ship, quality in ranked_ships.items():
    print(f"Ship {ship}: {quality}")

print("\nRanked Days of the Week by Quality of Prediction:")
for day, quality in ranked_days:
    print(f"Day {day}: {quality}")

print("\nImpact of Journey Count on Quality of Prediction:")
for count, quality in sorted_journey_count_quality.items():
    print(f"Journey Count {count}: {quality}")

