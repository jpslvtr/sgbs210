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
        if filename.endswith(".txt"):
            with open(os.path.join(folder_path, filename), 'r') as file:
                content = file.read()
                mse_over_time = extract_mse_over_time(content)
                days_of_week = extract_day_of_week(content)
                journey_count = content.count("Arrival Time:")

                if mse_over_time:
                    quality = mse_over_time[-1] - mse_over_time[0]

                    ship_id = filename.split('_')[0]
                    ship_quality[ship_id] = quality

                    for day in days_of_week:
                        day_quality[day].append(quality)

                    journey_count_quality.setdefault(journey_count, []).append(quality)

    # Average quality for each day of the week
    for day, qualities in day_quality.items():
        day_quality[day] = sum(qualities) / len(qualities) if qualities else 0

    # Average quality for each journey count
    for count, qualities in journey_count_quality.items():
        journey_count_quality[count] = sum(qualities) / len(qualities) if qualities else 0

    return ship_quality, day_quality, journey_count_quality

def print_analysis_results(results, description, output_file_name):
    ship_quality, day_quality, journey_count_quality = results

    with open(output_file_name, 'w') as output_file:
        output_file.write(f"{description}:\n")
        output_file.write("\nRanked Ships by Quality of Prediction:\n")
        for ship, quality in sorted(ship_quality.items(), key=lambda item: item[1], reverse=True):
            output_file.write(f"Ship {ship}: {quality}\n")

        output_file.write("\nRanked Days of the Week by Quality of Prediction:\n")
        for day, quality in sorted(day_quality.items(), key=lambda item: item[1], reverse=True):
            output_file.write(f"Day {day}: {quality:.4f}\n")

        output_file.write("\nImpact of Journey Count on Quality of Prediction:\n")
        for count, quality in sorted(journey_count_quality.items(), key=lambda item: item[1], reverse=True):
            output_file.write(f"Journey Count {count}: {quality:.4f}\n")

def main():
    result_folders = {
        '2_results': '../data_james/2_results',
        '3_results': '../data_james/3_results',
        '4_results': '../data_james/4_results'
    }

    for index, (description, folder_path) in enumerate(result_folders.items(), start=1):
        results = analyze_files(folder_path)
        output_file_name = f'results_{index}.txt'
        print_analysis_results(results, description, output_file_name)

if __name__ == '__main__':
    main()
