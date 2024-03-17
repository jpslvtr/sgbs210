import os
import json
from tqdm import tqdm

def process_ais_data(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    processed_mmsi = set()
    file_list = [f for f in os.listdir(input_folder) if f.endswith('.json')]
    
    for file_name in tqdm(file_list, desc="Processing files"):
        file_path = os.path.join(input_folder, file_name)
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            
            for entry in data:
                mmsi_number = str(entry.get('mmsi'))
                if mmsi_number not in processed_mmsi:
                    processed_mmsi.add(mmsi_number)
                output_file_path = os.path.join(output_folder, f"{mmsi_number}.txt")
                with open(output_file_path, 'a') as output_file:
                    output_file.write(f"File: {file_name}\n")
                    output_file.write(f"Record time: {entry.get('recordTime', 'N/A')}\n")
                    output_file.write(f"Event time: {entry.get('eventTime', 'N/A')}\n")
                    output_file.write(f"Status: {entry.get('status', 'N/A')}\n")
                    output_file.write(f"Time type: {entry.get('timeType', 'N/A')}\n")
                    output_file.write(f"Travel distance: {entry.get('travelDistance', 'N/A')}\n")
                    waypoints = entry.get('waypoints', [])
                    num_waypoints = len(waypoints)
                    output_file.write(f"Num waypoints: {num_waypoints}\n")
                    if waypoints:
                        output_file.write("Waypoints:\n")
                        for waypoint in waypoints:
                            coordinates = waypoint.get('coordinates', [])
                            output_file.write(f"- {coordinates[0]}, {coordinates[1]}\n")
                    output_file.write('\n')

if __name__ == '__main__':
    input_folder = '../data_master'
    output_folder = '../data_cleaned/ships_basic'
    process_ais_data(input_folder, output_folder)
