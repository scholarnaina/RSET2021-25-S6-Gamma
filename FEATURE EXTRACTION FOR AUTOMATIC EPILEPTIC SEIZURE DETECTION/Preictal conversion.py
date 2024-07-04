import os
import pandas as pd

# Define the folder containing the files
folder_path = '<path to folder containing csv files>'

# List of file names with seizure window information (assuming "start" key only)
file_list = [
    <dictionary containing file name, seizure start and end times>
]

# Dictionary to store the count of occurrences of each file name
file_counts = {}

# Loop through each file name in the file list
for index, file_info in enumerate(file_list):
    file_name = file_info["file_name"]  # Access "file_name" from the dictionary
    start_time = file_info["start"]

    # Update the count of occurrences for the current file name
    if file_name not in file_counts:
        file_counts[file_name] = 1
    else:
        file_counts[file_name] += 1

    # Define the output file path based on the current file being processed and its count
    count = file_counts[file_name]
    output_csv_frame1 = os.path.join(folder_path, f'{file_name}_frame{count}_1.csv')
    output_csv_frame2 = os.path.join(folder_path, f'{file_name}_frame{count}_2.csv')
    output_csv_frame3 = os.path.join(folder_path, f'{file_name}_frame{count}_3.csv')

    # Rest of the code for processing each file
    file_path = os.path.join(folder_path, file_name)
    print(f"Processing file: {file_name}")

    df = pd.read_csv(file_path)
    df['time'] = pd.to_numeric(df['time'])

    gap_start_time = start_time - 10
    frame1_start_time = gap_start_time - 10
    frame2_start_time = frame1_start_time - 10
    frame3_start_time = frame2_start_time - 10

    # Filter data for each frame
    frame1_data = df[(df['time'] >= frame1_start_time) & (df['time'] < gap_start_time)]
    frame2_data = df[(df['time'] >= frame2_start_time) & (df['time'] < frame1_start_time)]
    frame3_data = df[(df['time'] >= frame3_start_time) & (df['time'] < frame2_start_time)]

    # Save each frame to a separate CSV file
    frame1_data.to_csv(output_csv_frame1, index=False)
    frame2_data.to_csv(output_csv_frame2, index=False)
    frame3_data.to_csv(output_csv_frame3, index=False)

    print(f"Frame 1 data written to: {output_csv_frame1}")
    print(f"Frame 2 data written to: {output_csv_frame2}")
    print(f"Frame 3 data written to: {output_csv_frame3}")

    print("Processing complete.")
