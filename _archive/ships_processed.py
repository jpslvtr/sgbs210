import re
from datetime import datetime
import os
from tqdm import tqdm

def parse_record(record):
    # Extract the relevant fields from the record
    file_name = re.search(r'File: (.+\.json)', record).group(1)
    record_time = re.search(r'Record time: (.+)', record).group(1)
    event_time = re.search(r'Event time: (.+)', record).group(1)
    status = re.search(r'Status: (.+)', record).group(1)
    travel_distance = re.search(r'Travel distance: (.+)', record).group(1)
    waypoints = re.findall(r'- (\d+\.\d+), (\d+\.\d+)', record)
    waypoints = [(float(lat), float(lon)) for lat, lon in waypoints]
    return {
        'file_name': file_name,
        'record_time': record_time,
        'event_time': event_time,
        'status': status,
        'travel_distance': travel_distance,
        'waypoints': waypoints
    }

def format_record(record):
    # Format the waypoints as an array of pairs
    waypoints_formatted = ', '.join(str(wp) for wp in record['waypoints'])
    # Format the file names as a comma-separated list
    file_names_formatted = ', '.join(record['file_name'].split(', '))
    return f"Record time: {record['record_time']}\nEvent time: {record['event_time']}\nStatus: {record['status']}\nTravel distance: {record['travel_distance']}\nWaypoints: {waypoints_formatted}\nAssociated file(s): {file_names_formatted}\n"

def process_file(input_file, output_folder):
    with open(input_file, 'r') as f:
        content = f.read().strip()

    # Split the content into records and parse them
    excluded_statuses = {'NotMoving', 'UnableToPredict', 'DestinationChanged'}
    records = [parse_record(record) for record in content.split('\n\n') if not any(status in record for status in excluded_statuses)]


    # Sort records by record time
    records.sort(key=lambda r: datetime.strptime(r['record_time'], '%Y-%m-%dT%H:%M:%SZ'))

    # Combine records with identical record time and event time
    unique_records = {}
    for record in records:
        key = (record['record_time'], record['event_time'])
        if key not in unique_records:
            unique_records[key] = record
        else:
            unique_records[key]['file_name'] += ', ' + record['file_name']

    # Format the records
    formatted_records = [format_record(record) for record in unique_records.values()]

    # Determine the output file name
    base_name = os.path.basename(input_file)
    output_file = os.path.join(output_folder, f"{os.path.splitext(base_name)[0]}_processed.txt")

    # Write the output to a new file
    with open(output_file, 'w') as f:
        f.write('\n'.join(formatted_records))

def main():
    input_folder = '../data_cleaned/ships_basic'
    output_folder = '../data_cleaned/ships_processed'

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Get the list of input files
    input_files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if os.path.isfile(os.path.join(input_folder, f))]

    # Process each file
    for input_file in tqdm(input_files, desc="Processing files"):
        process_file(input_file, output_folder)

if __name__ == "__main__":
    main()
