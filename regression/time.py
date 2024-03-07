# Comments on the prediction quality of the time difference (dependent variable) based on the travel distance (independent variable) for each record within a journey.

# If we want to assess the accuracy of time estimates between records, leading up to arrival time

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
from datetime import datetime
import re

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


def perform_regression_analysis(df):
    X = df[['TravelDistance']].values.reshape(-1, 1)
    y = (df['EventTime'] - df['RecordTime']).dt.total_seconds() / 3600  # Convert to hours

    model = LinearRegression()
    model.fit(X, y)

    y_pred = model.predict(X)
    mse = mean_squared_error(y, y_pred)

    # Calculate MSE over time
    mse_over_time = []
    for i in range(1, len(X) + 1):
        y_pred_i = model.predict(X[:i])
        mse_i = mean_squared_error(y[:i], y_pred_i)
        mse_over_time.append(mse_i)

    return model.coef_[0], model.intercept_, mse, mse_over_time


def main():
    fp = '../data_james/ships_processed/422039900_processed.txt'
    # fp = '../data_james/ships_processed/677010900_processed.txt'
    # fp = '../data_james/ships_processed/677076600_processed.txt'
    # fp = '../data_james/ships_processed/525119020_processed.txt'
    with open(fp, 'r') as file:
        content = file.read()

    df = parse_data_from_text(content)
    # print("Dataframe after parsing:", df)
    print("Arrived count:", df[df['Status'] == 'Arrived'].shape[0])

    # Reverse DataFrame to work backwards from 'Arrived'
    df = df.iloc[::-1].reset_index(drop=True)

    # Mark each journey by cumulatively summing occurrences of 'Arrived'
    df['Journey'] = (df['Status'] == 'Arrived').cumsum()

    # Reverse DataFrame back to original order
    df = df.iloc[::-1].reset_index(drop=True)

    journeys = df.groupby('Journey')

    for journey_id, journey_df in journeys:
        print(f"\nAnalyzing journey {journey_id} with {len(journey_df)} records")
        underway_df = journey_df[journey_df['Status'] == 'Underway']
        if not underway_df.empty:
            coef, intercept, mse, mse_over_time = perform_regression_analysis(underway_df)
            print("Regression Analysis Results:")
            print(f"Model Coefficients: {coef}")
            print(f"Model Intercept: {intercept}")
            print(f"Mean Squared Error: {mse}")
            print("\nMSE over time (as ship approaches):")
            for i, mse_val in enumerate(mse_over_time, 1):
                print(f"Time Step {i}: MSE = {mse_val}")
        else:
            print("No 'Underway' records found for this journey, skipping regression analysis.")

if __name__ == '__main__':
    main()

