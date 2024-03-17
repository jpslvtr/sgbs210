import os
import re
from datetime import datetime
import pandas as pd
from tqdm import tqdm
import warnings

# Suppress FutureWarning across all modules
warnings.simplefilter(action='ignore', category=FutureWarning)

def parse_record(record, mmsi):
    # Extract the relevant fields from the record
    record_time = re.search(r'Record time: (.+)', record).group(1)
    event_time = re.search(r'Event time: (.+)', record).group(1)
    status = re.search(r'Status: (.+)', record).group(1)
    travel_distance = re.search(r'Travel distance: (.+)', record).group(1)
    waypoints = re.findall(r'- (\d+\.\d+), (\d+\.\d+)', record)
    waypoints = [(float(lat), float(lon)) for lat, lon in waypoints]
    
    try:
        record_time_dt = datetime.strptime(record_time, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        record_time_dt = datetime.strptime(record_time, "%Y-%m-%dT%H:%M:%SZ")
    day_of_week = record_time_dt.strftime('%A')  # Full weekday name
    
    return {
        'MMSI': mmsi,
        'RecordTime': record_time_dt.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'EventTime': event_time,
        'Status': status,
        'TravelDistance': travel_distance,
        'NumWaypoints': len(waypoints),
        'Waypoints': ', '.join([f"({lat}, {lon})" for lat, lon in waypoints]),
        'DayOfWeek': day_of_week,
    }

def process_file(input_file, output_folder):
    mmsi = os.path.splitext(os.path.basename(input_file))[0]
    with open(input_file, 'r') as f:
        content = f.read().strip()

    records = [parse_record(record, mmsi) for record in content.split('\n\n')]
    df = pd.DataFrame(records)
    
    # Exclude records with excluded statuses
    excluded_statuses = {'NotMoving', 'UnableToPredict', 'DestinationChanged'}
    df = df[~df['Status'].isin(excluded_statuses)]
    
    # Remove duplicate records based on RecordTime and EventTime
    df.drop_duplicates(subset=['RecordTime', 'EventTime'], inplace=True)

    # Sort records by record time
    df.sort_values(by='RecordTime', inplace=True)
    
    # Initialize journey number and valid journey flag
    df['Journey'] = 0
    journey_number = 0
    valid_journey = False

    for index, row in df.iterrows():
        if row['Status'] == 'Underway':
            valid_journey = True
            journey_number += 1
        elif row['Status'] == 'Arrived' and valid_journey:
            valid_journey = False  # Reset for the next journey
        else:
            continue  # Skip invalid 'Arrived' entries
        
        df.at[index, 'Journey'] = journey_number

    # Filter out records not part of a valid journey
    df = df[df['Journey'] > 0]
    
    # Count the number of unique journeys
    num_journeys = df[df['Status'] == 'Arrived']['Journey'].nunique()
    
    # Format and write the records to a file
    output_file_path = os.path.join(output_folder, f"{mmsi}_processed.txt")
    with open(output_file_path, 'w') as output_file:
        for _, row in df.iterrows():
            # output_file.write(f"MMSI: {row['MMSI']}\n")
            output_file.write(f"Record time: {row['RecordTime']}\n")
            output_file.write(f"Event time: {row['EventTime']}\n")
            output_file.write(f"Status: {row['Status']}\n")
            output_file.write(f"Travel distance: {row['TravelDistance']}\n")
            output_file.write(f"Num waypoints: {row['NumWaypoints']}\n")
            output_file.write(f"Waypoints: {row['Waypoints']}\n\n")
            # output_file.write(f"Day of Week: {row['DayOfWeek']}\n\n")
        # output_file.write(f"Number of Journeys: {num_journeys}\n")

def main():
    input_folder = '../data_cleaned/ships_basic'
    output_folder = '../data_cleaned/ships_processed'
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    input_files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith('.txt')]

    for input_file in tqdm(input_files, desc="Processing files"):
        process_file(input_file, output_folder)

if __name__ == "__main__":
    main()