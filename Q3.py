import json
from collections import defaultdict
from tabulate import tabulate

# Define the Series class to hold individual series information
class Series:
    def __init__(self, series_id, label, description):
        self.id = series_id
        self.label = label
        self.description = description
        self.observations = []

    def add_observation(self, date, value):
        self.observations.append({'d': date, 'v': value})

    def get_observations_by_date(self, start_date=None, end_date=None):
        filtered_observations = []
        for observation in self.observations:
            obs_date = observation['d']
            if start_date and obs_date < start_date:
                continue
            if end_date and obs_date > end_date:
                continue
            filtered_observations.append(observation)
        return filtered_observations

# Define the Output class to hold multiple Series objects and provide aggregated data
class Output:
    def __init__(self, series_objects, series_ids):
        self.series_objects = {series_id: series_objects[series_id] for series_id in series_ids if series_id in series_objects}

    def get_aggregated_observations_by_date(self, start_date=None, end_date=None):
        aggregated_observations = defaultdict(int)
        for series in self.series_objects.values():
            observations = series.get_observations_by_date(start_date, end_date)
            for observation in observations:
                date = observation['d']
                value = float(observation['v'])
                aggregated_observations[date] += value
        return {date: value for date, value in sorted(aggregated_observations.items())}
# Create a function to initialize Series objects from the JSON data
def initialize_series_from_json(json_data):
    series_objects = {}
    for series_id, series_info in json_data.get('seriesDetail', {}).items():
        label = series_info.get('label', '')
        description = series_info.get('description', '')
        series_objects[series_id] = Series(series_id, label, description)
    
    # Add observations to the corresponding Series objects
    for observation in json_data.get('observations', []):
        date = observation.get('d')
        for series_id, value_info in observation.items():
            if series_id == 'd':  # Skip the date entry
                continue
            value = value_info.get('v')
            if series_id in series_objects:
                series_objects[series_id].add_observation(date, value)
    
    return series_objects



# Data Structure
x = [
    ("Personal loan plan loans", ["V36867"]),
    ("Credit card loans", ["V36868"]),
    ("Personal lines of credit", ["V36869"]),
    ("Other personal loans", ["V36870"]),
    ("Chartered bank deposits, personal, chequable", ["V41552775"]),
    ("Chartered bank deposits, personal, non-chequable, notice", ["V36821", "V36822"]),
    ("Chartered bank deposits, personal, term, tax sheltered", ["V36824"]),
    ("Chartered bank deposits, personal, term, other", ["V36825"]),
    ("Chartered bank deposits, non-personal, chequable", ["V41552777"]),
    ("Chartered bank deposits, non-personal, non-chequable", ["V36828"]),
    ("Chartered bank deposits, non-personal, term", ["V36830"]),
    ("Total, foreign currency deposits of Canadian residents", ["V36872"]),
    ("Advances from the Bank of Canada", ["V36634"]),
    ("Canadian dollar assets, total", ["V36852"]),
    ("Non-mortgage loans, total", ["V36855"]),
    ("Mortgages, total", ["V36857"])
]

files =["c2.json", "c1.json", "b2.json"]
series_objects = {}
for file in files:
    with open(file, 'r') as f:
        json_data = json.load(f)
    temp = initialize_series_from_json(json_data)
    series_objects = series_objects | temp

# Initialize Output objects based on the provided data structure
output_objects = {}
for name, series_ids in x:
    output_objects[name] = Output(series_objects, series_ids)

# Desired dates
desired_dates = ["2023-07-01", "2020-01-01"]

# Initialize a dictionary to hold the observations table data for the desired dates
table_data_filtered = defaultdict(dict)

# Fill the table data with observations only for the desired dates
for name, output_obj in output_objects.items():
    observations = output_obj.get_aggregated_observations_by_date()
    for date in desired_dates:
        value = observations.get(date, 'N/A')
        table_data_filtered[name][date] = value

# Convert the table data to a list of lists for tabulation
table_list_filtered = [['Row Name'] + sorted(desired_dates) + ["% increase in growth"]]
for row_name, observations in table_data_filtered.items():
    row = [row_name]
    for date in table_list_filtered[0][1:-1]:
        row.append(observations.get(date, 'N/A'))
    if row[1] != 'N/A' and row[2] != 'N/A':
        row.append(round((row[2] - row[1]) / row[1] * 100,1))
    table_list_filtered.append(row)

# Convert the 2D array to a tab-separated string
table_tab_separated = '"\n"'.join(['","'.join(map(str, row)) for row in table_list_filtered])

# Print the tab-separated string for the user to copy and paste into Excel
print(table_tab_separated)
# Generate and return the table
table_str_filtered = tabulate(table_list_filtered, headers='firstrow', tablefmt='pipe')
print(table_str_filtered)