import pandas as pd
# Define the directory path
Path = <add your path here>
# Construct the full file path
file_path = <add path to csv file>
# Read the CSV file using the full file path
df = pd.read_csv(file_path)
print("\nHEAD")
# Print the DataFrame
print(df.head(2))
print("\nTail")
print(df.tail(2)) #specify the number of rows to be visualised
