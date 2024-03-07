# Predicting distance traveled by ship

import os
import re
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from tqdm import tqdm


def parse_data_from_text(content):
    pattern = re.compile(
        r"Record time: (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z).*?Event time: (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d+Z).*?Status: (Underway|Arrived).*?Travel distance: ([\d.]+)",
        re.DOTALL,
    )
    records = []
    for match in pattern.finditer(content):
        record_time, event_time, status, travel_distance = match.groups()
        if travel_distance and status == "Underway":
            record_time = datetime.strptime(record_time, "%Y-%m-%dT%H:%M:%SZ")
            event_time = datetime.strptime(event_time, "%Y-%m-%dT%H:%M:%S.%fZ")
            travel_distance = float(travel_distance)
            time_diff = (
                event_time - record_time
            ).total_seconds() / 3600  # Convert to hours
            records.append((time_diff, travel_distance))
    return pd.DataFrame(records, columns=["TimeDiff", "TravelDistance"])


def perform_regression_analysis(df):
    X = df[["TimeDiff"]]
    y = df["TravelDistance"]

    model = LinearRegression()
    model.fit(X, y)

    y_pred = model.predict(X)
    mse = mean_squared_error(y, y_pred)

    mse_over_time = []
    for i in range(1, len(X) + 1):
        y_pred_i = model.predict(X.iloc[:i])
        mse_i = mean_squared_error(y.iloc[:i], y_pred_i)
        mse_over_time.append(mse_i)

    return model, mse, mse_over_time


def main():
    directory = "../data_james/ships_processed"
    output_file = "out.txt"

    with open(output_file, "w") as mse_file:
        for filename in tqdm(os.listdir(directory)):
            if filename.endswith("_processed.txt"):
                mmsi = filename.split("_")[0]
                mse_file.write(f"MMSI: {mmsi}\n")

                fp = os.path.join(directory, filename)
                with open(fp, "r") as file:
                    content = file.read()

                df = parse_data_from_text(content)
                if not df.empty:
                    model, mse, mse_over_time = perform_regression_analysis(df)
                    mse_file.write(f"Model Coefficients: {model.coef_}\n")
                    mse_file.write(f"Model Intercept: {model.intercept_}\n")
                    mse_file.write(f"MSE: {mse}\n")
                    for i, mse_val in enumerate(mse_over_time, 1):
                        mse_file.write(f"Time Step {i}: MSE = {mse_val}\n")
                    mse_file.write("\n")
                else:
                    mse_file.write("No valid data found for regression analysis.\n\n")


if __name__ == "__main__":
    main()
