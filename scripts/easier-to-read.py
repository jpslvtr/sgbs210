import json
import os

def format_ship_data(input_directory, output_directory):
    # Ensure the output directory exists
    os.makedirs(output_directory, exist_ok=True)

    # Process each JSON file in the input directory
    for filename in os.listdir(input_directory):
        if filename.endswith('.json'):
            print(f"Processing file: {filename}")
            input_filepath = os.path.join(input_directory, filename)

            # Extract the date and time part from the filename
            date_time_part = '_'.join(filename.split('_')[2:]).split('.')[0]

            # Construct the output filename
            output_filename = date_time_part + '.txt'
            output_filepath = os.path.join(output_directory, output_filename)

            with open(input_filepath, 'r') as file:
                data = json.load(file)

            formatted_data = []
            for entry in data:
                formatted_entry = "Ship name: {}\n".format(entry['ship']['name'])
                formatted_entry += "MMSI: {}\n".format(entry['mmsi'])
                formatted_entry += "Record time: {}\n".format(entry['recordTime'])
                formatted_entry += "Event time: {}\n".format(entry.get('eventTime', 'Not Applicable'))
                formatted_entry += "Status: {}\n".format(entry['status'])
                formatted_entry += "Time type: {}\n".format(entry['timeType'])
                formatted_entry += "Travel distance: {}\n".format(entry.get('travelDistance', 'Not Applicable'))
                formatted_entry += "\n"
                formatted_data.append(formatted_entry)

            with open(output_filepath, 'w') as file:
                file.writelines(formatted_data)
            print(f"Output written to: {output_filename}")

# Example usage
input_directory = '../data_subset/json'
output_directory = '../data_subset/simplified'
format_ship_data(input_directory, output_directory)
