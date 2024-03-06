import folium
from folium import FeatureGroup, LayerControl
import re
from tqdm import tqdm

# Function to parse the file and extract relevant data
def parse_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    # Split the content by 'File:' to separate each record
    records = content.split('File:')[1:]

    # Define a pattern to match latitude and longitude in waypoints
    waypoint_pattern = re.compile(r'-\s(\d+\.\d+),\s(\d+\.\d+)')

    # List to hold parsed data
    data = []

    for record in records:
        # Extracting relevant information using regular expressions
        file_name = re.search(r'api_response_(.*?).json', record).group(1)
        record_time = re.search(r'Record time: (.*?)Z', record).group(1)
        
        # Updated regex to handle optional milliseconds
        event_time_match = re.search(r'Event time: (.*?)(\.\d+)?Z', record)
        if event_time_match:
            event_time = event_time_match.group(1)
        else:
            # Handle cases where Event time might be missing or in a different format
            event_time = 'N/A'  # Or some other placeholder value

        status = re.search(r'Status: (\w+)', record).group(1)
        time_type = re.search(r'Time type: (\w+)', record).group(1)
        waypoints = waypoint_pattern.findall(record)

        # Convert string waypoints to float tuples and swap the order to (latitude, longitude)
        waypoints = [(float(lon), float(lat)) for lat, lon in waypoints]

        # Append to data list
        data.append({
            'file_name': file_name,
            'record_time': record_time,
            'event_time': event_time,
            'status': status,
            'time_type': time_type,
            'waypoints': waypoints
        })

    return data

def plot_journey(data):
    # Initialize the map at the first waypoint of the first record with waypoints
    initial_location = None
    for record in data:
        if record['waypoints']:
            initial_location = record['waypoints'][0]
            break
    
    if not initial_location:
        print("No waypoints found in the data.")
        return
    
    folium_map = folium.Map(location=initial_location, zoom_start=5)

    # Define a list of colors to cycle through
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred',
              'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue',
              'darkpurple', 'white', 'pink', 'lightblue', 'lightgreen',
              'gray', 'black', 'lightgray']
    color_index = 0

    # Loop through each record and plot the waypoints with a progress bar
    for record in tqdm(data, desc="Plotting journey"):
        if not record['waypoints']:
            continue

        # Use the record time as the label for the route
        route_label = f"Route {record['record_time']}"

        # Create a feature group for each route, labeled by record time
        route_group = FeatureGroup(name=route_label)

        # Select color for the current route and update the color index
        color = colors[color_index % len(colors)]
        color_index += 1

        # Add waypoints to the feature group
        for waypoint in record['waypoints']:
            folium.Marker(
                location=waypoint,
                popup=f"{record['file_name']}<br>Record Time: {record['record_time']}<br>Event Time: {record['event_time']}<br>Status: {record['status']}",
                icon=folium.Icon(color=color)
            ).add_to(route_group)

        # Connect waypoints with lines in the feature group
        folium.PolyLine(record['waypoints'], color=color).add_to(route_group)

        # Add the feature group to the map
        route_group.add_to(folium_map)

    # Add layer control to the map to toggle routes
    LayerControl().add_to(folium_map)

    folium_map.save('../ship_journey.html')


if __name__ == '__main__':
    file_path = '../data_james/ships/269047000.txt'
    journey_data = parse_file(file_path)
    plot_journey(journey_data)