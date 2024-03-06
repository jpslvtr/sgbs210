import os
import json
from tqdm import tqdm

def find_ship_data(mmsi_number, input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    output_file_path = os.path.join(output_folder, f"{mmsi_number}.txt")
    
    file_list = [f for f in os.listdir(input_folder) if f.endswith('.json')]
    with open(output_file_path, 'w') as output_file:
        for file_name in tqdm(file_list, desc="Processing"):
            file_path = os.path.join(input_folder, file_name)
            
            with open(file_path, 'r') as json_file:
                data = json.load(json_file)
                
                for entry in data:
                    if str(entry.get('mmsi')) == str(mmsi_number):
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
    mmsi_number = '269047000'
    input_folder = '../data_james/data_master'
    output_folder = '../data_james/ships'
    find_ship_data(mmsi_number, input_folder, output_folder)
