import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from datetime import datetime
import re
import os
from tqdm import tqdm

def parse_data_from_text(content, ship_id, total_journeys):
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
            time_diff = (event_time - record_time).total_seconds() / 3600  # Convert to hours
            day_of_week = record_time.weekday()
            records.append({
                "RecordTime": record_time, 
                "EventTime": event_time, 
                "Status": status, 
                "TimeDiff": time_diff,
                "TravelDistance": travel_distance,
                "DayOfWeek": day_of_week,
                "ShipID": ship_id,
                "TotalJourneys": total_journeys
            })

    return pd.DataFrame(records)

def perform_space_regression(df):
    X = df[["TimeDiff"]]
    y = df["TravelDistance"]

    model = LinearRegression()
    model.fit(X, y)

    y_pred = model.predict(X)
    mse = mean_squared_error(y, y_pred)

    # Calculate MSE over time
    mse_over_time = []
    for i in range(1, len(X) + 1):
        y_pred_i = model.predict(X.iloc[:i])
        mse_i = mean_squared_error(y.iloc[:i], y_pred_i)
        mse_over_time.append(mse_i)

    # Extract the coefficients and intercept
    coef = model.coef_[0]
    intercept = model.intercept_

    return coef, intercept, mse, mse_over_time

def perform_time_regression(df):
    X = df[['TravelDistance', 'DayOfWeek', 'ShipID', 'TotalJourneys']]
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
    input_folder = '../data_james/ships_processed'
    output_folder = '../data_james/regression_results_v2'

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    input_files = [f for f in os.listdir(input_folder) if f.endswith('_processed.txt')]

    for input_file in tqdm(input_files, desc="Processing files"):
        ship_id = int(input_file.split('_')[0])  # Assuming the file name format is "shipID_rest_of_the_file_name.txt"
        file_path = os.path.join(input_folder, input_file)
        with open(file_path, 'r') as file:
            content = file.read()
            total_journeys = content.count("Status: Arrived")

        df = parse_data_from_text(content, ship_id, total_journeys)
        if not df.empty:
            df = df.iloc[::-1].reset_index(drop=True)
            # Correctly initialize and increment journey numbers
            df['Journey'] = df['Status'].eq('Arrived').shift(1, fill_value=False).cumsum() + 1
            df = df.iloc[::-1].reset_index(drop=True)
            journeys = df.groupby('Journey')

            total_journeys = len(journeys)
            results = {}

            for journey_id, journey_df in journeys:
                new_journey_id = total_journeys - journey_id + 1
                analysis_output = f"Analyzing journey {new_journey_id} with {len(journey_df)} records"
                if 'Arrived' in journey_df['Status'].values:
                    arrival_time = journey_df[journey_df['Status'] == 'Arrived']['EventTime'].iloc[0]
                    analysis_output += f"\nArrival Time: {arrival_time}\n"
                else:
                    analysis_output += "\nNo 'Arrival Time' found for this journey, skipping regression analysis.\n"
                    analysis_output += "\n=================================\n\n"
                    results[journey_id] = analysis_output
                    continue  # Skip to the next journey
                underway_df = journey_df[journey_df['Status'] == 'Underway']
                if not underway_df.empty:
                    # Perform time regression
                    time_coef, time_intercept, time_mse, time_mse_over_time = perform_time_regression(underway_df)
                    analysis_output += "\n=== Predicting Time Estimates ==="
                    analysis_output += f"\nModel Coefficients: {time_coef}"
                    analysis_output += f"\nModel Intercept: {time_intercept}"
                    analysis_output += f"\nMean Squared Error (MSE): {time_mse}"
                    analysis_output += "\nMSE over time (as ship approaches):"
                    for i, mse_val in enumerate(time_mse_over_time, 1):
                        analysis_output += f"\nTime Step {i}: MSE = {mse_val}"

                    # Perform space regression
                    space_coef, space_intercept, space_mse, space_mse_over_time = perform_space_regression(underway_df)
                    analysis_output += "\n\n=== Predicting Travel Estimates ==="
                    analysis_output += f"\nModel Coefficients: {space_coef}"
                    analysis_output += f"\nModel Intercept: {space_intercept}"
                    analysis_output += f"\nMean Squared Error (MSE): {space_mse}"
                    analysis_output += "\nMSE over time (as ship approaches):"
                    for i, mse_val in enumerate(space_mse_over_time, 1):
                        analysis_output += f"\nTime Step {i}: MSE = {mse_val}"
                    analysis_output += "\n\n"
                else:
                    analysis_output += "\nNo 'Underway' records found for this journey, skipping regression analysis.\n\n"

                analysis_output += "=================================\n\n"
                results[journey_id] = analysis_output

            output_file_path = os.path.join(output_folder, input_file.replace('_processed.txt', '_regression.txt'))
            with open(output_file_path, 'w') as output_file:
                for journey_id in sorted(results.keys(), reverse=True):
                    output_file.write(results[journey_id])

if __name__ == '__main__':
    main()