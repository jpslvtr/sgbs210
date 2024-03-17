import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from datetime import datetime
import re
import os
from tqdm import tqdm
from sklearn.model_selection import train_test_split

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
            time_diff = (event_time - record_time).total_seconds() / 3600  # Convert to hours
            records.append({
                "RecordTime": record_time, 
                "EventTime": event_time, 
                "Status": status, 
                "TimeDiff": time_diff,
                "TravelDistance": travel_distance
            })

    return pd.DataFrame(records)

def identify_journeys(df):
    # Initialize the journey number
    df['Journey'] = 0
    journey_number = 0

    for i, row in df.iterrows():
        if row['Status'] == 'Underway' and journey_number == 0:
            # Start the first journey with the first 'Underway' record
            journey_number = 1
        df.at[i, 'Journey'] = journey_number
        if row['Status'] == 'Arrived':
            # Increment the journey number after each 'Arrived' status
            journey_number += 1

    return df

def perform_space_regression(df):
    if len(df) < 5:  # Adjust this threshold as necessary
        return None, None, None, None

    X = df[['TimeDiff']].values.reshape(-1, 1)
    y = df['TravelDistance']

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)

    mse_over_time = []
    for i in range(1, len(X_test) + 1):
        y_pred_i = model.predict(X_test[:i])
        mse_i = mean_squared_error(y_test[:i], y_pred_i)
        mse_over_time.append(mse_i)

    return model.coef_[0], model.intercept_, mse, mse_over_time

def perform_time_regression(df):
    if len(df) < 5:  # Ensure there are enough records to split, 5 is arbitrary, adjust as needed
        return None, None, None, None

    X = df[['TravelDistance']].values.reshape(-1, 1)
    y = (df['EventTime'] - df['RecordTime']).dt.total_seconds() / 3600

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)

    mse_over_time = []
    for i in range(1, len(X_test) + 1):
        y_pred_i = model.predict(X_test[:i])
        mse_i = mean_squared_error(y_test[:i], y_pred_i)
        mse_over_time.append(mse_i)

    return model.coef_[0], model.intercept_, mse, mse_over_time


def main():
    input_folder = '../data_cleaned/ships_processed'
    output_folder = '../data_cleaned/1_results'

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    input_files = [f for f in os.listdir(input_folder) if f.endswith('_processed.txt')]

    for input_file in tqdm(input_files, desc="Processing files"):
        file_path = os.path.join(input_folder, input_file)
        with open(file_path, 'r') as file:
            content = file.read()

        df = parse_data_from_text(content)
        if not df.empty:
            df = identify_journeys(df)
            journeys = df.groupby('Journey')

            results = {}

            for journey_id, journey_df in journeys:
                analysis_output = f"Analyzing journey {journey_id} with {len(journey_df)} records\n"
                
                if len(journey_df) < 5:
                    analysis_output += "Insufficient data for regression analysis. Skipping this journey.\n"
                    analysis_output += "=================================\n\n"
                    results[journey_id] = analysis_output
                    continue

                if 'Arrived' in journey_df['Status'].values:
                    arrival_time = journey_df[journey_df['Status'] == 'Arrived']['EventTime'].iloc[0]
                    analysis_output += f"Arrival Time: {arrival_time}\n"
                else:
                    analysis_output += "No 'Arrival Time' found for this journey, skipping regression analysis.\n"
                    analysis_output += "=================================\n\n"
                    results[journey_id] = analysis_output
                    continue

                # Proceed with regression analysis only if there are enough 'Underway' records
                underway_df = journey_df[journey_df['Status'] == 'Underway']
                if len(underway_df) < 5:
                    analysis_output += "Insufficient 'Underway' records for regression analysis. Skipping this journey.\n"
                    analysis_output += "=================================\n\n"
                    results[journey_id] = analysis_output
                    continue

                # Perform time regression
                time_coef, time_intercept, time_mse, time_mse_over_time = perform_time_regression(underway_df)
                if time_coef is not None:
                    analysis_output += "\n=== Predicting Time Estimates ==="
                    analysis_output += f"\nModel Coefficients: {time_coef}"
                    analysis_output += f"\nModel Intercept: {time_intercept}"
                    analysis_output += f"\nMean Squared Error (MSE): {time_mse}"
                    analysis_output += "\nMSE over time (as ship approaches):"
                    for i, mse_val in enumerate(time_mse_over_time, 1):
                        analysis_output += f"\nTime Step {i}: MSE = {mse_val}"
                else:
                    analysis_output += "\nInsufficient data for time regression analysis.\n"

                # Perform space regression
                space_coef, space_intercept, space_mse, space_mse_over_time = perform_space_regression(underway_df)
                if space_coef is not None:
                    analysis_output += "\n\n=== Predicting Travel Estimates ==="
                    analysis_output += f"\nModel Coefficients: {space_coef}"
                    analysis_output += f"\nModel Intercept: {space_intercept}"
                    analysis_output += f"\nMean Squared Error (MSE): {space_mse}"
                    analysis_output += "\nMSE over time (as ship approaches):"
                    for i, mse_val in enumerate(space_mse_over_time, 1):
                        analysis_output += f"\nTime Step {i}: MSE = {mse_val}"
                else:
                    analysis_output += "\nInsufficient data for space regression analysis.\n"

                analysis_output += "\n=================================\n\n"
                results[journey_id] = analysis_output

            output_file_path = os.path.join(output_folder, input_file.replace('_processed.txt', '_1.txt'))
            with open(output_file_path, 'w') as output_file:
                for journey_id in sorted(results.keys()):
                    output_file.write(results[journey_id])


            output_file_path = os.path.join(output_folder, input_file.replace('_processed.txt', '_1.txt'))
            with open(output_file_path, 'w') as output_file:
                for journey_id in sorted(results.keys()):
                    output_file.write(results[journey_id])

if __name__ == '__main__':
    main()