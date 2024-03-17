import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
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

def identify_journeys(df):
    df['Journey'] = 0
    journey_number = 1

    for i, row in df.iterrows():
        df.at[i, 'Journey'] = journey_number
        if row['Status'] == 'Arrived':
            journey_number += 1

    return df

def perform_space_regression(df):
    if len(df) < 5:  # Ensure there are enough records to split
        return None, None, None, None

    X = df[["TimeDiff"]]
    y = df["TravelDistance"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)

    mse_over_time = []
    for i in range(1, len(X_test) + 1):
        y_pred_i = model.predict(X_test.iloc[:i])
        mse_i = mean_squared_error(y_test.iloc[:i], y_pred_i)
        mse_over_time.append(mse_i)

    return model.coef_[0], model.intercept_, mse, mse_over_time

def perform_time_regression(df):
    if len(df) < 5:  # Ensure there are enough records to split
        return None, None, None

    X = df[['TravelDistance', 'DayOfWeek', 'ShipID', 'TotalJourneys']]
    y = (df['EventTime'] - df['RecordTime']).dt.total_seconds() / 3600

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = DecisionTreeRegressor(random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)

    mse_over_time = []
    for i in range(1, len(X_test) + 1):
        y_pred_i = model.predict(X_test[:i])
        mse_i = mean_squared_error(y_test[:i], y_pred_i)
        mse_over_time.append(mse_i)

    feature_importances = model.feature_importances_

    return feature_importances, mse, mse_over_time

def main():
    input_folder = '../data_cleaned/ships_processed'
    output_folder = '../data_cleaned/3_results'

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    input_files = [f for f in os.listdir(input_folder) if f.endswith('_processed.txt')]

    for input_file in tqdm(input_files, desc="Processing files"):
        ship_id = int(re.search(r'^(\d+)_', input_file).group(1))  # Assuming the file name format is "shipID_rest_of_the_file_name.txt"
        file_path = os.path.join(input_folder, input_file)
        with open(file_path, 'r') as file:
            content = file.read()
            total_journeys = content.count("Status: Arrived")

        df = parse_data_from_text(content, ship_id, total_journeys)
        if not df.empty:
            df = identify_journeys(df)
            journeys = df.groupby('Journey')

            results = {}

            for journey_id, journey_df in journeys:
                analysis_output = f"Analyzing journey {journey_id} with {len(journey_df)} records\n"
                if 'Arrived' in journey_df['Status'].values:
                    arrival_time = journey_df[journey_df['Status'] == 'Arrived']['EventTime'].iloc[0]
                    analysis_output += f"\nArrival Time: {arrival_time}\n"
                else:
                    analysis_output += "\nNo 'Arrival Time' found for this journey, skipping regression analysis.\n"
                    analysis_output += "=================================\n\n"
                    results[journey_id] = analysis_output
                    continue

                underway_df = journey_df[journey_df['Status'] == 'Underway']
                if len(underway_df) >= 5:
                    time_feature_importances, time_mse, time_mse_over_time = perform_time_regression(underway_df)
                    analysis_output += "\n=== Decision Tree Time Regression ==="
                    analysis_output += f"\nFeature Importances: {time_feature_importances}"
                    analysis_output += f"\nMean Squared Error (MSE): {time_mse}"
                    analysis_output += "\nMSE over time (as ship approaches):"
                    for i, mse_val in enumerate(time_mse_over_time, 1):
                        analysis_output += f"\nTime Step {i}: MSE = {mse_val}"

                    # Space regression analysis is not performed with DecisionTreeRegressor, adjust as needed
                else:
                    analysis_output += "\nNo 'Underway' records found for this journey, skipping regression analysis.\n\n"

                analysis_output += "\n\n=================================\n\n"
                results[journey_id] = analysis_output

            output_file_path = os.path.join(output_folder, input_file.replace('_processed.txt', '_3.txt'))
            with open(output_file_path, 'w') as output_file:
                for journey_id in sorted(results.keys()):
                    output_file.write(results[journey_id])

if __name__ == '__main__':
    main()
