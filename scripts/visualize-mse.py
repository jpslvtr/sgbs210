import os
import re
import matplotlib.pyplot as plt
from tqdm import tqdm
import numpy as np

# Base directory where the data folders are located
base_dir = '../data_cleaned'
# Subdirectories for different regression analyses
sub_dirs = ['1_results', '2_results', '3_results', '4_results']
# Labels for the plots
labels = ['Linear Regression (1 Var)', 'Linear Regression (Multi Var)', 'Regression Tree', 'Random Forest']
# Dictionary to store MSE values
mse_values = {label: [] for label in labels}

# Regular expression pattern to match MSE lines
mse_pattern = re.compile(r'Mean Squared Error \(MSE\):\s+(\d+\.\d+)')

# Iterate over each subdirectory and file
for sub_dir, label in zip(sub_dirs, labels):
    full_path = os.path.join(base_dir, sub_dir)
    files = os.listdir(full_path)
    for filename in tqdm(files, desc=f'Processing {label}'):
        try:
            with open(os.path.join(full_path, filename), 'rb') as file:
                for line in file:
                    # Decode each line with UTF-8 and replace undecodable bytes
                    line = line.decode('utf-8', 'replace')
                    match = mse_pattern.search(line)
                    if match:
                        mse_values[label].append(float(match.group(1)))
        except UnicodeDecodeError:
            print(f"Skipping file {filename} due to a decoding error.")

# Print statistics
for label in labels:
    data = mse_values[label]
    if data:
        print(f"\nStatistics for {label}:")
        print(f"Mean MSE: {np.mean(data):.4f}")
        print(f"Median MSE: {np.median(data):.4f}")
        print(f"Standard Deviation MSE: {np.std(data):.4f}")
        print(f"Min MSE: {np.min(data):.4f}")
        print(f"Max MSE: {np.max(data):.4f}")
    else:
        print(f"\nNo MSE values found for {label}.")

# Plotting
fig, ax = plt.subplots()
ax.boxplot(mse_values.values(), labels=labels, patch_artist=True)
ax.set_title('Comparison of MSE Across Regression Analyses')
ax.set_ylabel('Mean Squared Error (MSE)')
ax.set_xlabel('Type of Regression Analysis')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()