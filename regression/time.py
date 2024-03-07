# Comments on the prediction quality of the time difference (dependent variable) based on the travel distance (independent variable) for each record within a journey.

# If we want to assess the accuracy of time estimates between records, leading up to arrival time

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from datetime import datetime
import re
import os
from tqdm import tqdm

# Function to parse data from text
def parse_data_from_text(content):
    records_split = re.split(r'\n(?=Record time:)', content.strip())
    pattern = re.compile(
        r"Record time: (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)\s*?Event time: (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z)\s*?Status: (\w+)(?:\s*?Travel distance: ([\d.]+|N/A))?",
        re.DOTALL,
    )
    records = []
    for record in records_split:
        match = pattern.search(record)
        if match:
            record_time, event_time, status, travel_distance = match.groups()
            record_time = datetime.strptime(record_time, "%Y-%m-%dT%H:%M:%SZ")
            try:
                event_time = datetime.strptime(event_time, "%Y-%m-%dT%H:%M:%S.%fZ")
            except ValueError:
                event_time = datetime.strptime(event_time, "%Y-%m-%dT%H:%M:%SZ")
            travel_distance = None if travel_distance == "N/A" else float(travel_distance)

            records.append({
                "RecordTime": record_time,
                "EventTime": event_time,
                "Status": status,
                "TravelDistance": travel_distance
            })

    return pd.DataFrame(records)

# Function to perform regression analysis
def perform_regression_analysis(df):
    X = df[['TravelDistance']].values.reshape(-1, 1)
    y = (df['EventTime'] - df['RecordTime']).dt.total_seconds() / 3600

    model = LinearRegression()
    model.fit(X, y)

    y_pred = model.predict(X)
    mse = mean_squared_error(y, y_pred)

    mse_over_time = []
    for i in range(1, len(X) + 1):
        y_pred_i = model.predict(X[:i])
        mse_i = mean_squared_error(y[:i], y_pred_i)
        mse_over_time.append(mse_i)

    return model.coef_[0], model.intercept_, mse, mse_over_time

def main():
    # # fp = '../data_james/ships_processed/422039900_processed.txt'
    # fp = '../data_james/ships_processed/677010900_processed.txt'
    # # fp = '../data_james/ships_processed/677076600_processed.txt'
    # # fp = '../data_james/ships_processed/525119020_processed.txt'
    # with open(fp, 'r') as file:
    #     content = file.read()

    # df = parse_data_from_text(content)
    # df = df.iloc[::-1].reset_index(drop=True)
    # df['Journey'] = (df['Status'] == 'Arrived').cumsum()
    # df = df.iloc[::-1].reset_index(drop=True)
    # journeys = df.groupby('Journey')

    # total_journeys = len(journeys)

    # # Store the results in a dictionary
    # results = {}

    # for journey_id, journey_df in journeys:
    #     new_journey_id = total_journeys - journey_id + 1
    #     analysis_output = f"\nAnalyzing journey {new_journey_id} with {len(journey_df)} records"
    #     arrival_time = journey_df[journey_df['Status'] == 'Arrived']['EventTime'].iloc[0] if 'Arrived' in journey_df['Status'].values else 'No arrival time'
    #     analysis_output += f"\nArrival Time: {arrival_time}"
    #     underway_df = journey_df[journey_df['Status'] == 'Underway']
    #     if not underway_df.empty:
    #         coef, intercept, mse, mse_over_time = perform_regression_analysis(underway_df)
    #         analysis_output += "\n=== Predicting Time Estimates ==="
    #         analysis_output += f"\nModel Coefficients: {coef}"
    #         analysis_output += f"\nModel Intercept: {intercept}"
    #         analysis_output += f"\nMean Squared Error (MSE): {mse}"
    #         analysis_output += "\n\nMSE over time (as ship approaches):"
    #         for i, mse_val in enumerate(mse_over_time, 1):
    #             analysis_output += f"\nTime Step {i}: MSE = {mse_val}"
    #     else:
    #         analysis_output += "\nNo 'Underway' records found for this journey, skipping regression analysis."
        
    #     # Store the output for each journey
    #     results[journey_id] = analysis_output

    # # Print the results in the desired order
    # for journey_id in sorted(results.keys(), reverse=True):
    #     print(results[journey_id])

    input_folder = '../data_james/ships_processed'
    output_folder = '../data_james/regression_results/time'

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    input_files = [f for f in os.listdir(input_folder) if f.endswith('_processed.txt')]

    for input_file in tqdm(input_files, desc="Processing files"):
        file_path = os.path.join(input_folder, input_file)
        with open(file_path, 'r') as file:
            content = file.read()

        df = parse_data_from_text(content)
        if not df.empty:
            df = df.iloc[::-1].reset_index(drop=True)
            df['Journey'] = (df['Status'] == 'Arrived').cumsum()
            df = df.iloc[::-1].reset_index(drop=True)
            journeys = df.groupby('Journey')

            total_journeys = len(journeys)
            results = {}

            for journey_id, journey_df in journeys:
                new_journey_id = total_journeys - journey_id + 1
                analysis_output = f"Analyzing journey {new_journey_id} with {len(journey_df)} records"
                arrival_time = journey_df[journey_df['Status'] == 'Arrived']['EventTime'].iloc[0] if 'Arrived' in journey_df['Status'].values else 'No arrival time'
                analysis_output += f"\nArrival Time: {arrival_time}"
                underway_df = journey_df[journey_df['Status'] == 'Underway']
                if not underway_df.empty:
                    coef, intercept, mse, mse_over_time = perform_regression_analysis(underway_df)
                    analysis_output += "\n=== Predicting Time Estimates ==="
                    analysis_output += f"\nModel Coefficients: {coef}"
                    analysis_output += f"\nModel Intercept: {intercept}"
                    analysis_output += f"\nMean Squared Error (MSE): {mse}"
                    analysis_output += "\nMSE over time (as ship approaches):"
                    for i, mse_val in enumerate(mse_over_time, 1):
                        analysis_output += f"\nTime Step {i}: MSE = {mse_val}"
                    analysis_output += "\n\n"
                else:
                    analysis_output += "\nNo 'Underway' records found for this journey, skipping regression analysis."

                results[journey_id] = analysis_output

            output_file_path = os.path.join(output_folder, input_file.replace('_processed.txt', '_regression_time.txt'))
            with open(output_file_path, 'w') as output_file:
                for journey_id in sorted(results.keys(), reverse=True):
                    output_file.write(results[journey_id])

if __name__ == '__main__':
    main()

