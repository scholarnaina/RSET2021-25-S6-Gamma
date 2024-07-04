import csv
from scipy.signal import welch
import datetime


def calculate_relative_band_power(data, column, band_range, fs=256, window='hann', overlap=0.5):

  total_power = 0
  band_power = 0
  signal = []
  start_time =<enter start of seizure>
  end_time =  <enter end time of seizure>
  for row in data:
    current_time = float(row['time'])  # Assuming 'time' is the column with timestamps

    # Check if within seizure period (remove pre-defined times here)
    if start_time <= current_time <= end_time:
      # Within seizure period, accumulate data for Welch's method
      value = float(row[column])
      signal.append(value)

  if len(signal) > 0:
    # Apply Welch's method to calculate PSD (even with negative values)
    freqs, psd = welch(signal, fs=fs, window=window, noverlap=overlap)

    # Integrate power within the band
    for i, f in enumerate(freqs):
      if band_range[0] <= f <= band_range[1]:
        band_power += abs(psd[i])  # Use absolute value to include negative power
      total_power += abs(psd[i])  # Use absolute value for total power

    # Calculate relative power within the band
    if total_power > 0:
      return band_power / total_power
    else:
      return None  # No data within seizure period for this electrode
  else:
    return None  # No data within seizure period for this electrode


def main():
  # Replace 'drive/MyDrive/EEG' with the actual path to your EEG data directory
  Path = 'drive/MyDrive/EEG'


  # Open and process the CSV file
  with open(f'{Path}<filepath>', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    data = list(reader)

  # Get all column names except 'time'
  electrode_columns = [col for col in reader.fieldnames if col not in ['time']]

  # Define beta wave frequency range
  alpha_range=(8,12)
  delta_range = (0.5,4)

  # Loop through each electrode and calculate relative beta power
  print("\nALPHA")
  for column in electrode_columns:
    relative_alpha_power = calculate_relative_band_power(data, column, alpha_range)

    if relative_alpha_power is not None:
      print(f"{column}: {relative_alpha_power:.2f}")

  print("\nDELTA")
  for column in electrode_columns:
    relative_delta_power = calculate_relative_band_power(data, column, delta_range)
    if relative_delta_power is not None:
      print(f"{column}: {relative_delta_power:.2f}")
if __name__ == "__main__":
  main()