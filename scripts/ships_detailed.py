# Only extracts estimates for records that are underway or arrived / make a prediction about arrival

from tqdm import tqdm
import os

def parse_file(input_file):
    data = []
    with open(input_file, 'r') as f:
        lines = f.readlines()
        current_record = {}
        parsing_waypoints = False
        for line in lines:
            line = line.strip()
            if line.startswith("File:"):
                if current_record:
                    data.append(current_record)
                current_record = {"file": line.split(": ")[1]}
                parsing_waypoints = False
            elif line.startswith("Record time:"):
                current_record["record_time"] = line.split(": ")[1]
            elif line.startswith("Event time:"):
                current_record["event_time"] = line.split(": ")[1]
            elif line.startswith("Status:"):
                current_record["status"] = line.split(": ")[1]
            elif line.startswith("Time type:"):
                current_record["time_type"] = line.split(": ")[1]
            elif line.startswith("Travel distance:"):
                distance_str = line.split(": ")[1]
                current_record["travel_distance"] = float(distance_str) if distance_str != "N/A" else "N/A"
            elif line.startswith("Num waypoints:"):
                current_record["num_waypoints"] = int(line.split(": ")[1])
                current_record["waypoints"] = []
                parsing_waypoints = True
            elif parsing_waypoints and line.startswith("-"):
                current_record["waypoints"].append(tuple(map(float, line[1:].split(", "))))
            elif parsing_waypoints and not line.startswith("-"):
                parsing_waypoints = False
        if current_record:
            data.append(current_record)
    return data

def process_data(data):
    estimates = []
    arrivals = []
    estimate_groups = {}

    for record in data:
        if record["status"] == "Underway":
            estimate_key = (record["record_time"], record["event_time"], record["travel_distance"], record["num_waypoints"])
            if estimate_key not in estimate_groups:
                estimate_groups[estimate_key] = {
                    "files": [record["file"]],
                    "record_time": record["record_time"],
                    "event_time": record["event_time"],
                    "travel_distance": record["travel_distance"],
                    "num_waypoints": record["num_waypoints"],
                    "waypoints": record["waypoints"]
                }
            else:
                estimate_groups[estimate_key]["files"].append(record["file"])
        elif record["status"] == "Arrived":
            arrivals.append({
                "file": record["file"],
                "record_time": record["record_time"],
                "event_time": record["event_time"],
                "status": record["status"],
                "time_type": record["time_type"],
                "travel_distance": "N/A",
                "num_waypoints": 0
            })

    for estimate in estimate_groups.values():
        estimates.append(estimate)

    return estimates, arrivals

def write_output(output_file, estimates, arrivals):
    with open(output_file, 'w') as f:
        for i, estimate in enumerate(estimates, start=1):
            f.write(f"Estimate {i}:\n")
            f.write(f"Files: {', '.join(estimate['files'])}\n")
            f.write(f"Record time: {estimate['record_time']}\n")
            f.write(f"Event time: {estimate['event_time']}\n")
            f.write(f"Travel distance: {estimate['travel_distance']}\n")
            f.write(f"Num waypoints: {estimate['num_waypoints']}\n")
            f.write("\n")
        
        f.write("Arrivals:\n")
        for arrival in arrivals:
            f.write(f"File: {arrival['file']}\n")
            f.write(f"Record time: {arrival['record_time']}\n")
            f.write(f"Event time: {arrival['event_time']}\n")
            f.write(f"Status: {arrival['status']}\n")
            f.write(f"Time type: {arrival['time_type']}\n")
            f.write(f"Travel distance: {arrival['travel_distance']}\n")
            f.write(f"Num waypoints: {arrival['num_waypoints']}\n")
            f.write("\n")

def process_files(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    input_files = os.listdir(input_folder)
    for input_file in tqdm(input_files):
        if input_file.endswith('.txt'):
            input_path = os.path.join(input_folder, input_file)
            output_path = os.path.join(output_folder, input_file.replace('.txt', '_processed.txt'))
            data = parse_file(input_path)
            estimates, arrivals = process_data(data)
            write_output(output_path, estimates, arrivals)

def main():
    input_folder = '../data_james/ships_basic'
    output_folder = '../data_james/ships_detailed'
    process_files(input_folder, output_folder)

if __name__ == "__main__":
    main()
