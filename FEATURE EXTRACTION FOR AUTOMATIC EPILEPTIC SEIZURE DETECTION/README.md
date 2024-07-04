# Feature Extraction for Automatic Epileptic Seizure Detection from EEG Signals

This project aims to develop an automated system for identifying preictal stages and detecting epileptic seizures using EEG data. The focus is on extracting features, particularly analyzing relative alpha and delta wave changes critical for seizure onset detection and progression monitoring.

## System Overview

The system includes a graphical user interface (GUI) designed to facilitate medical professionals in visualizing and interpreting EEG data in CSV format. This interface enhances accessibility and aids in making informed clinical decisions.

## System Features

### User Authentication

User authentication ensures secure access to sensitive patient data. Upon successful login, authenticated users can upload EEG data files, which are converted to CSV format for efficient processing and integration with machine learning models. Unauthorized access attempts are met with error messages to maintain data integrity and patient confidentiality.

### File Upload Facility

The software allows users to upload EEG data files, which are then converted into CSV format. This conversion is crucial for the efficient implementation of machine learning models and data analysis.

### Highlighting Channels under Variation

After conversion to CSV format, the system analyzes EEG channel values to identify patterns indicative of epileptic seizures. Channels showing significant variation are highlighted, aiding medical practitioners in pinpointing regions of abnormal brain activity. This feature utilizes power spectrum analysis and other techniques to quantify EEG signals accurately.

### Returning the Time-Frame of Suspected Epileptic Activity

The system scrutinizes CSV files channel-by-channel to identify the time frame of suspected epileptic activity, segmenting data into preictal, ictal, and interictal periods. This precise temporal information is crucial for diagnosing and managing seizures effectively.

## Installation

Clone the repository:

```bash
git clone https://github.com/NiyathaVS/EEG-Seizure-Detection.git
cd EEG-Seizure-Detection


Usage
Access the GUI by running a Python script.
Enter valid credentials to access the GUI.
Upload EEG data files in CSV format for visualization and analysis.
Contributing
Contributions to this project are welcome! Please fork the repository, create a new branch, make your changes, and submit a pull request.

License
This project is licensed under the auspices of Rajagiri School Of Engineering And Technology, ensuring adherence to ethical standards and best practices in medical software development.
