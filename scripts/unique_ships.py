import json
import glob
from tqdm import tqdm

def find_unique_ships(folder_path):
    json_files = glob.glob(f"{folder_path}/*.json")
    unique_ships = {}

    # Process all files with a single tqdm progress bar
    for file_path in tqdm(json_files, desc="Processing JSON files"):
        with open(file_path, 'r') as file:
            try:
                data = json.load(file)
                # Handle both list and dictionary data structures
                if isinstance(data, list):
                    for item in data:
                        mmsi = item['ship']['mmsi']
                        ship_name = item['ship']['name']
                        unique_ships[mmsi] = ship_name
                else:
                    mmsi = data['ship']['mmsi']
                    ship_name = data['ship']['name']
                    unique_ships[mmsi] = ship_name
            except Exception as e:
                # Skip files that cause errors
                continue

    return unique_ships

if __name__ == '__main__':
    folder_path = '../data_james/data_master' 
    ships = find_unique_ships(folder_path)
    for mmsi, name in ships.items():
        print(f"{mmsi}, ")
    
    print(f"Total unique ships found: {len(ships)}")