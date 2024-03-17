import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import re

# Function to extract MSE values from result files
def extract_mse_from_results(file_path):
    mse_values = []
    with open(file_path, 'r') as file:
        for line in file:
            if 'Mean Squared Error (MSE):' in line:
                mse = float(line.split(':')[-1].strip())
                mse_values.append(mse)
    return mse_values

# Function to read analysis results and return a DataFrame
def read_analysis_results(file_path):
    data = {'Ship': [], 'Quality': [], 'Day': [], 'DayQuality': [], 'JourneyCount': [], 'JourneyQuality': []}
    current_section = ''
    with open(file_path, 'r') as file:
        for line in file:
            if 'Ranked Ships by Quality of Prediction:' in line:
                current_section = 'ship'
            elif 'Ranked Days of the Week by Quality of Prediction:' in line:
                current_section = 'day'
            elif 'Impact of Journey Count on Quality of Prediction:' in line:
                current_section = 'journey'
            else:
                if current_section == 'ship' and ':' in line:
                    ship, quality = line.split(':')
                    data['Ship'].append(ship.strip())
                    data['Quality'].append(float(quality.strip()))
                elif current_section == 'day' and ':' in line:
                    day, quality = line.split(':')
                    data['Day'].append(day.strip())
                    data['DayQuality'].append(float(quality.strip()))
                elif current_section == 'journey' and ':' in line:
                    count, quality = line.split(':')
                    data['JourneyCount'].append(count.strip())
                    data['JourneyQuality'].append(float(quality.strip()))

    # Ensure all lists in the dictionary have the same length
    max_length = max(len(lst) for lst in data.values())
    for key in data:
        data[key].extend([None] * (max_length - len(data[key])))

    return pd.DataFrame(data)
# Directory paths
results_dir = '../data_cleaned'
analysis_dir = '../analysis'

day_quality_data = []
journey_quality_data = []

for i in [2, 4]:  # Adjusted to only include models 2 and 4
    analysis_data = read_analysis_results(f'{analysis_dir}/results_{i}.txt')
    
    # Extracting Day of the Week Quality data
    for day, quality in zip(analysis_data['Day'], analysis_data['DayQuality']):
        if pd.notna(day) and pd.notna(quality):
            day_quality_data.append({'Model': f'Model {i}', 'Day': day, 'Quality': quality})
    
    # Extracting Journey Count Quality data
    for count, quality in zip(analysis_data['JourneyCount'], analysis_data['JourneyQuality']):
        if pd.notna(count) and pd.notna(quality):
            # Remove the word 'Journey' and convert to integer
            count = int(count.replace('Journey Count ', ''))
            journey_quality_data.append({'Model': f'Model {i}', 'JourneyCount': count, 'Quality': quality})

day_quality_df = pd.DataFrame(day_quality_data)
journey_quality_df = pd.DataFrame(journey_quality_data)

# Plotting Day of the Week Quality for models 2 and 4
plt.figure(figsize=(10, 6))
sns.barplot(x='Day', y='Quality', hue='Model', data=day_quality_df)
plt.title('Day of the Week Quality of Prediction Across Models 2 and 4')
plt.ylabel('Quality of Prediction')
plt.xlabel('Day of the Week')
plt.legend(title='Model')
plt.show()

# Plotting Impact of Journey Count on Quality for models 2 and 4
plt.figure(figsize=(10, 6))
sns.lineplot(x='JourneyCount', y='Quality', hue='Model', data=journey_quality_df, marker='o')
plt.title('Impact of Journey Count on Quality of Prediction Across Models 2 and 4')
plt.ylabel('Quality of Prediction')
plt.xlabel('Number of Journeys')
# Set x-axis ticks to be the unique sorted journey counts
plt.xticks(sorted(journey_quality_df['JourneyCount'].unique()))
plt.legend(title='Model')
plt.show()

