import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Define the paths to the directories containing the result and analysis files
results_dir = '../data_james'
analysis_dir = '../analysis'

# Define the pattern to match the result files for models 1-4
result_file_patterns = [
    os.path.join(results_dir, '1_results', '*.txt'),
    os.path.join(results_dir, '2_results', '*.txt'),
    os.path.join(results_dir, '3_results', '*.txt'),
    os.path.join(results_dir, '4_results', '*.txt')
]

# Define the pattern to match the analysis files for models 2-4
analysis_file_patterns = [
    os.path.join(analysis_dir, 'results_2.txt'),
    os.path.join(analysis_dir, 'results_3.txt'),
    os.path.join(analysis_dir, 'results_4.txt')
]

# Function to extract MSE values from a result file
def extract_mse(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        mse_values = []
        for line in lines:
            if 'Mean Squared Error (MSE):' in line:
                mse = float(line.split()[-1])
                mse_values.append(mse)
        return mse_values

# Function to extract analysis data from an analysis file
def extract_analysis_data(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
        # Implement parsing logic based on the structure of the analysis files
        # This is a placeholder for the actual parsing logic
        analysis_data = {}
        return analysis_data

# Read and process result files for each model
all_mse_values = []
for i, pattern in enumerate(result_file_patterns, start=1):
    mse_values = []
    for file_path in glob.glob(pattern):
        mse_values.extend(extract_mse(file_path))
    all_mse_values.append(mse_values)

# Read and process analysis files for models 2-4
all_analysis_data = []
for file_path in analysis_file_patterns:
    analysis_data = extract_analysis_data(file_path)
    all_analysis_data.append(analysis_data)

# Visualization of MSE comparison across models (1-4)
plt.boxplot(all_mse_values, labels=[f'Model {i}' for i in range(1, 5)])
plt.title('MSE Comparison Across Models')
plt.ylabel('MSE')
plt.show()

# Analysis of the effect of MMSI, day of the week, and number of journeys on each model (2-4)
# Placeholder for the actual analysis and visualization code
# You would need to implement the logic based on the structure of the analysis data

# For example, if analysis_data is a DataFrame, you could use seaborn to create visualizations
# sns.barplot(x='MMSI', y='MSE', data=analysis_data)
# plt.show()