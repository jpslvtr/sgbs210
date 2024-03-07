import matplotlib.pyplot as plt
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import numpy as np
from datetime import datetime
import re

def parse_data_from_text(content):
    pattern = re.compile(r'Record time: (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z).*?Event time: (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d+Z).*?Travel distance: ([\d.]+|N/A)', re.DOTALL)
    records = []
    for match in pattern.finditer(content):
        record_time, event_time, travel_distance = match.groups()
        if travel_distance != 'N/A':
            record_time = datetime.strptime(record_time, '%Y-%m-%dT%H:%M:%SZ')
            event_time = datetime.strptime(event_time, '%Y-%m-%dT%H:%M:%S.%fZ')
            travel_distance = float(travel_distance)
            time_diff = (event_time - record_time).total_seconds() / 3600  # Convert to hours
            records.append((time_diff, travel_distance))
    return pd.DataFrame(records, columns=['TimeDiff', 'TravelDistance'])

def perform_regression_analysis(df):
    X = df[['TimeDiff']]
    y = df['TravelDistance']
    
    model = LinearRegression()
    model.fit(X, y)
    
    y_pred = model.predict(X)
    mse = mean_squared_error(y, y_pred)
    
    # Plot actual vs predicted travel distance
    plt.scatter(X, y, color='blue', label='Actual')
    plt.plot(X, y_pred, color='red', label='Predicted')
    plt.title('Actual vs Predicted Travel Distance')
    plt.xlabel('Time Difference (hours)')
    plt.ylabel('Travel Distance')
    plt.legend()
    plt.show()
    
    # Calculate and plot MSE over time
    mse_over_time = []
    for i in range(1, len(X) + 1):
        y_pred_i = model.predict(X.iloc[:i])
        mse_i = mean_squared_error(y.iloc[:i], y_pred_i)
        mse_over_time.append(mse_i)
    
    plt.plot(range(1, len(X) + 1), mse_over_time, color='green')
    plt.title('MSE over Time')
    plt.xlabel('Time Step')
    plt.ylabel('MSE')
    plt.show()
    
    return model, mse, mse_over_time

def main():
    fp = '../data_james/ships_detailed/422039900_processed.txt'
    with open(fp, 'r') as file:
        content = file.read()
    
    df = parse_data_from_text(content)
    if not df.empty:
        model, mse, mse_over_time = perform_regression_analysis(df)
        print(f'Model Coefficients: {model.coef_}')
        print(f'Model Intercept: {model.intercept_}')
        print(f'MSE: {mse}')
        print("MSE over time:")
        for i, mse_val in enumerate(mse_over_time, 1):
            print(f"Time Step {i}: MSE = {mse_val}")
    else:
        print("No valid data found for regression analysis.")


if __name__ == '__main__':
    main()
