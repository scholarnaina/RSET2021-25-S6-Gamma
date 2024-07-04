import os
import pandas as pd

# Define the folder containing the files
folder_path = '<path to your folder containing the csv files>'

# List of file names with seizure window information
file_list = [
    <dictionary with filename, seizure start and end times>
]

# Path of the output CSV file
output_csv = f'<add path to your csv file to be processed>'

# Loop through each file information dictionary in the list
for file_info in file_list:
  file_name = file_info["file_name"]
  file_path = os.path.join(folder_path, file_name)
  print(f"Processing file: {file_name}")

  # Read the CSV file using pandas
  df = pd.read_csv(file_path)

  # Extract start and end times from seizure window information
  start_time = file_info["start"]
  end_time = file_info["end"]
  print(f"Seizure window: {start_time} - {end_time} seconds")

  # Convert seconds to timestamps (considering sampling rate of 1 kHz)
  time_stamps = (df['time'] >= start_time) & (df['time'] <= end_time)

  # Filter the DataFrame based on the time window
  df_windowed = df[time_stamps]

  # Write directly with column names in to_csv()
  df_windowed.to_csv(output_csv, mode='a', header=df_windowed.columns, index=False)
  print(f"Filtered data written to: {output_csv}")