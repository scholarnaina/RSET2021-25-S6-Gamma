import tkinter as tk
from tkinter import *
from tkinter import Tk, filedialog, Label, Entry, Button, Frame, Text, messagebox, colorchooser
import matplotlib.pyplot as plt
from mne.io import read_raw_edf
from datetime import datetime
import mne
import os
import csv
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def check_credentials(username, password):
    """
    This function checks the username and password against the credentials.csv file.

    Args:
        username: The username entered by the user.
        password: The password entered by the user.

    Returns:
        True if the credentials match a record in the CSV file, False otherwise.
    """
    try:
        with open("credentials.csv", 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if username == row[0] and password == row[1]:
                    return True
            return False
    except FileNotFoundError:
        messagebox.showerror("Error", "Credentials file 'credentials.csv' not found.")
        return False

class LoginPage:
    def __init__(self, master):
        self.data = None
        self.table = None
        self.master = master
        master.title("Login Page")
        master.geometry("640x440")

        self.username_label = tk.Label(master, text="Username", height=3, width=20, font=(20))
        self.username_label.pack()

        self.username_entry = tk.Entry(master, font=("Arial", 16))
        self.username_entry.pack()

        self.password_label = tk.Label(master, text="Password", height=3, width=20, font=(20))
        self.password_label.pack()

        self.password_entry = tk.Entry(master, show="*", font=("Arial", 16))
        self.password_entry.pack()

        self.submit_button = tk.Button(master, text="Submit", command=self.submit_login, height=3, width=15, font=(20))
        self.submit_button.pack(pady=20)

    def submit_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if check_credentials(username, password):
            messagebox.showinfo("Success", "Login Successful!")
            self.master.after(2000, self.redirect_to_edf_visualizer)  # Redirect after 2 seconds
        else:
            messagebox.showerror("Error", "Invalid username or password")

    def redirect_to_edf_visualizer(self):
        self.master.destroy()
        root = tk.Tk()
        app = EDFVisualizerApp(root)
        root.mainloop()

class EDFVisualizerApp:
    def __init__(self, master):
        self.master = master
        self.data = None
        self.table = None
        master.title("File Upload and Visualize")
        master.geometry("600x400")  # Window size

        self.file_path = ""

        self.file_path_label = tk.Label(master, text="No file selected")
        self.file_path_label.pack()

        self.select_file_button = tk.Button(master, text="Select EDF File", command=self.select_file)
        self.select_file_button.pack(padx=10, pady=10)

        self.visualize_edf_graph_button = tk.Button(master, text="Visualize EDF Graph", command=self.visualize_edf_graph)
        self.visualize_edf_graph_button.pack(padx=10, pady=10)

        self.convert_to_csv_button = tk.Button(master, text="Convert EDF to CSV", command=self.convert_to_csv)
        self.convert_to_csv_button.pack(padx=10, pady=10)

        self.visualize_csv_graph_button = tk.Button(master, text="Upload and Visualize CSV Graph", command=self.visualize_csv_graph)
        self.visualize_csv_graph_button.pack(padx=10, pady=10)

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("EDF files", "*.edf")])
        if file_path:
            self.file_path_label.config(text=file_path)
            self.file_path = file_path

    def convert_to_csv(self):
        if self.file_path:
            edf_file = mne.io.read_raw_edf(self.file_path)
            csv_file = os.path.splitext(self.file_path)[0] + '.csv'
            edf_file.to_data_frame().to_csv(csv_file, index=False)
            messagebox.showinfo("Success", f"EDF file converted to CSV: {csv_file}")
        else:
            messagebox.showerror("Error", "Please select an EDF file first.")

    def visualize_edf_graph(self):
        if self.file_path:
            try:
                raw = mne.io.read_raw_edf(self.file_path)
                channels = raw.ch_names
                selected_channels = self.select_channels(channels)
                if selected_channels:
                    self.plot_line_graph(raw, selected_channels)
            except Exception as e:
                messagebox.showerror("Error", str(e))
        else:
            messagebox.showerror("Error", "Please select an EDF file first.")

    def select_channels(self, channels):
        selected = []
        popup = tk.Toplevel()
        popup.geometry("800x800")
        popup.title("Select Channels")
        tk.Label(popup, text="Select the channels for display:").pack()

        def add_channel(channel_var):
            if channel_var.get() not in selected:
                selected.append(channel_var.get())

        def select_all():
            for checkbox in checkboxes:
                checkbox.select()
                add_channel(checkbox.var)

        checkboxes = []
        for channel in channels:
            var = tk.StringVar()
            checkbox = tk.Checkbutton(popup, text=channel, variable=var, onvalue=channel, offvalue="", command=lambda v=var: add_channel(v))
            checkbox.pack()
            checkbox.var = var  # Store var in the checkbox object
            checkboxes.append(checkbox)

        select_all_button = tk.Button(popup, text="Select All", command=select_all,height=5)
        select_all_button.pack()

        ok_button = tk.Button(popup, text="OK", command=popup.destroy, height=10, width=10)
        ok_button.pack(pady=20)

        popup.wait_window()
        return selected
    

    def plot_line_graph(self, raw, selected_channels):
        popup = tk.Toplevel()
        popup.title("Line Graphs - Channels")
        popup.geometry("800x600")

        canvas = tk.Canvas(popup, width=780, height=580)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)

        scrollbar_y = tk.Scrollbar(popup, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.configure(yscrollcommand=scrollbar_y.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=frame, anchor=tk.NW)

        fig_height = len(selected_channels) * 2

        fig, axs = plt.subplots(len(selected_channels), 1, figsize=(15, fig_height))

        for idx, channel in enumerate(selected_channels):
            data, times = raw[channel, :]
            axs[idx].plot(times, data.T)
            axs[idx].set_xlabel('Time (s)')
            axs[idx].set_ylabel('Amplitude (uV)')
            axs[idx].set_title(f'Line Graph - Channel {channel}')
            axs[idx].grid(True)
       
        plt.tight_layout()

        canvas_image = FigureCanvasTkAgg(fig, master=frame)
        canvas_image.get_tk_widget().pack()

        canvas.config(scrollregion=canvas.bbox("all"))

    def visualize_csv_graph(self):
        root = tk.Tk()
        eeg_visualizer = EEGDataVisualizer(root)
        root.mainloop()
        
class EEGDataVisualizer:
    def __init__(self, master):
        self.master = master
        master.geometry("900x900")
        master.title("EEG Data Visualizer (**Safety Note: This is for visualization only, not medical diagnosis**)")

        # Emphasize safety note:
        self.safety_label = Label(master, text="",font=("TkDefaultFont", 10, "bold"))
        self.safety_label.pack()

        #patient folder selection
        self.folder_label = tk.Label(master, text="Select Patient Folder:",font=(4))
        self.folder_label.place(x=40, y=10)

        self.folder_entry = tk.Entry(master,width=40)
        self.folder_entry.place(x=250, y=10)

        self.select_folder_button = tk.Button(master, text="Select Folder", command=self.select_folder,font=(4))
        self.select_folder_button.place(x=350, y=35)

        # File path label and input
        self.file_path_label = Label(master, text="Select CSV File:", font=(10))
        self.file_path_label.pack()
        self.file_path_entry = Entry(master, width=50)
        self.file_path_entry.pack()
        self.browse_button = Button(master, text="Browse...", command=self.browse_file, font=(5))
        self.browse_button.pack()

        # Time Section (using grid layout)
        time_label = Label(master, text="Start Time (HH:MM:SS):", font=(10))
        time_label.pack()

        time_frame = Frame(master)
        time_frame.pack()

        self.start_time_hour_entry = Entry(time_frame, width=3)
        self.start_time_hour_entry.pack(side="left")
        self.start_time_minute_entry = Entry(time_frame, width=3)
        self.start_time_minute_entry.pack(side="left")
        self.start_time_second_entry = Entry(time_frame, width=3)
        self.start_time_second_entry.pack(side="left")

        # Optional End Time Section (using grid layout)
        end_time_label = Label(master, text="End Time (HH:MM:SS):", font=(10))
        end_time_label.pack()

        end_time_frame = Frame(master)
        end_time_frame.pack()

        self.end_time_hour_entry = Entry(end_time_frame, width=3)
        self.end_time_hour_entry.pack(side="left")
        self.end_time_minute_entry = Entry(end_time_frame, width=3)
        self.end_time_minute_entry.pack(side="left")
        self.end_time_second_entry = Entry(end_time_frame, width=3)
        self.end_time_second_entry.pack(side="left")

        # Sampling Frequency Section
        sampling_freq_label = Label(master, text="Sampling Frequency:", font=(10))
        sampling_freq_label.pack()

        self.sampling_freq_entry = Entry(master, width=10)
        self.sampling_freq_entry.pack()

        # Seizure Start and End Time Section
        seizure_label = Label(master, text="Seizure Start Time (seconds):", font=(10))
        seizure_label.pack()

        seizure_frame = Frame(master)
        seizure_frame.pack()

        self.seizure_start_entry = Entry(seizure_frame, width=10)
        self.seizure_start_entry.pack(side="left")

        seizure_label = Label(master, text="Seizure End Time (seconds):", font=(10))
        seizure_label.pack()

        seizure_frame = Frame(master)
        seizure_frame.pack()

        self.seizure_end_entry = Entry(seizure_frame, width=10)
        self.seizure_end_entry.pack(side="left")

        # Highlight button
        self.highlight_button = Button(master, text="Highlight", command=self.highlight_seizure, font=(5))
        self.highlight_button.place(x=950,y=300)

        # Reset button
        self.reset_button = Button(master, text="Reset Graph", command=self.reset_graph, font=(10))
        self.reset_button.place(x=950,y=770)

        # Comment box
        self.comment_label = Label(master, text="Enter Comments:", font=(5))
        self.comment_label.place(x=40,y=40)


        self.comment_entry = Text(master,height=5,width=50)
        self.comment_entry.place(x=40, y=80)

        # Enter button for comments
        self.enter_button = Button(master, text="Enter", command=self.enter_comments, font=(10))
        self.enter_button.place(x=450,y=130)

        # Text box for previous data
        self.previous_data_label = Label(master, text="Previous Data:", font=(10))
        self.previous_data_label.place(x=40,y=170)

        self.previous_data_entry = Text(master, height=7, width=50)
        self.previous_data_entry.place(x=40,y=200)

        # Plot canvas
        self.figure = plt.figure(figsize=(8, 4))
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
             
        # Print button
        self.print_button = Button(master, text="Print", command=self.save_to_pdf, font=(60))
        self.print_button.place(x=1200,y=770)

        # Visualize button
        self.visualize_button = Button(master, text="Visualize", command=self.visualize, height=3, width=10, font=(20))
        self.visualize_button.pack()

        # Initialize highlighted region data
        self.highlighted_data = []


    def select_folder(self):
        try:
            patient_folder = filedialog.askdirectory(title="Select Patient Folder")
            if patient_folder:
                self.folder_entry.delete(0, tk.END)
                self.folder_entry.insert(0, patient_folder)

                # Check for patient_data.csv existence
                csv_file_path = os.path.join(patient_folder, "patient_data.csv")
                if os.path.exists(csv_file_path):
                    self.file_path_entry.delete(0, tk.END)
                    self.file_path_entry.insert(0, csv_file_path)
                else:
                    # Create the CSV file
                    comments = self.comment_entry.get("1.0", "end-1c")  # Retrieve comments from Text widget
                    current_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.save_comments_to_csv(comments, current_date_time)
                    with open(csv_file_path, 'w', newline='') as csvfile:
                        writer = csv.writer(csvfile)
                        #writer.writerow(["time","signal"])
                        writer.writerow([current_date_time, comments])
            
                    messagebox.showinfo("CSV File Created", "patient_data.csv created successfully.")

        except Exception as e:
            messagebox.showerror("Error", f"Error selecting folder: {e}")

    def enter_comments(self):
        comments = self.comment_entry.get("1.0", "end-1c")  # Retrieve comments from Text widget
        current_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.save_comments_to_csv(comments, current_date_time)
        
    def load_previous_data(self):
        try:
            folder_path = self.folder_entry.get()
            csv_file_name = "patient_data.csv"
            # Create the full path to the CSV file
            csv_file_path = os.path.join(folder_path, csv_file_name)
            print(csv_file_path)
            with open(csv_file_path, "r") as f:
                reader = csv.reader(f)
                previous_data = []
                for row in reader:
                    data=','.join(row)
                    previous_data.append(data)
                #for row in reader:
                    #previous_data.append(row[1])   Assuming comments are in the second column

                previous_data = "\n".join(previous_data)
                self.previous_data_entry.insert("1.0", previous_data)
        except FileNotFoundError:
            print("Previous data file not found.")

    def retrieve_patient_data(self):
        folder_path = self.folder_entry.get()
        csv_file_name = "patient_data.csv"
        # Create the full path to the CSV file
        csv_file_path = os.path.join(folder_path, csv_file_name)
        print(csv_file_path)
        if os.path.isfile(csv_file_path):
            self.file_path_entry.delete(0, "end")
            self.file_path_entry.insert(0, file_name)
            self.load_previous_data(file_name)

        print(f"CSV file created successfully: {csv_file_path}")

    def save_comments_to_csv(self, comments, current_date_time):
        try:
            folder_path = self.folder_entry.get()
            csv_file_name = "patient_data.csv"
            # Create the full path to the CSV file
            csv_file_path = os.path.join(folder_path, csv_file_name)
            with open(csv_file_path, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([current_date_time, comments])
                print("Comments saved to CSV successfully!")
        except Exception as e:
            print(f"Error saving comments to CSV: {e}")

    def save_to_pdf(self):
        try:
            file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
            if file_path:
                self.figure.savefig(file_path)
                print("Figure saved to PDF successfully!")
            else:
                print("Save operation cancelled.")
        except Exception as e:
            print(f"Error saving figure to PDF: {e}")

    '''def save_to_pdf(self) -> None:
        try:
            file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
            if file_path:
                self.figure.savefig(file_path)
                print("Figure saved to PDF successfully!")

                # Add data from previous data box and comment box entry to the PDF
                previous_data = self.previous_data_entry.get("1.0", "end-1c")
                comments = self.comment_entry.get("1.0", "end-1c")

                # Create a PDF file object                
                pdf = canvas.Canvas(file_path, pagesize=(612, 792))  # A4 size

                # Add previous data to the PDF
                pdf.setFont("Helvetica", 12)
                pdf.drawString(50, 750, "Previous Data:\n")
                line_height = 20  # Set the desired line height
                y_position = 730 - line_height
                for line in previous_data.split("\n"):
                    pdf.drawString(50, y_position, line)
                    y_position -= line_height
                    if y_position<100:
                        pdf.newPage()

                # Add comments to the PDF
                pdf.drawString(50, y_position, "Comments:\n")
                y_position_1 = y_position - line_height
                for line in comments.split("\n"):
                    pdf.drawString(50, y_position_1, line)
                    y_position_1 -= line_height
                    if y_position_1<100:
                        pdf.newPage()

                # Save the PDF
                pdf.save()

        except Exception as e:
            print(f"Error saving figure to PDF: {e}")'''
  

    def browse_file(self):
        self.file_path = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv")]
        )
        self.file_path_entry.delete(0, "end")
        self.file_path_entry.insert(0, self.file_path)
        self.load_previous_data()

    def highlight_seizure(self):
        try:
            start_time = float(self.seizure_start_entry.get())
            end_time = float(self.seizure_end_entry.get())

            # Get file path
            file_path = self.file_path_entry.get()

            # Get sampling frequency
            sampling_freq = float(self.sampling_freq_entry.get())

            # Read EEG data from CSV file
            with open(file_path, "r") as f:
                reader = csv.reader(f)
                timestamps = []
                eeg_data = []  # Assuming a single EEG channel
                next(reader)
                next(reader)
                for row in reader:
                    timestamps.append(eval(row[0]))  # Assuming time is in the first column
                    eeg_data.append(eval(row[1]))  # Assuming EEG data is in the second column

            # Calculate number of data points to display based on sampling frequency and time
            start_index = int(start_time * sampling_freq)
            end_index = min(int(end_time * sampling_freq), len(timestamps))
            #print(start_time,end_time)
            #print(start_index,end_index)

            # Choose color for highlighting
            color = colorchooser.askcolor()[1]
            self.axes.plot(timestamps[start_index:end_index + 1], eeg_data[start_index:end_index + 1],color = color)
            self.canvas.draw()  # Update the plot
           
        except ValueError as ve:
            print(f"**Error: {ve}**")
        except Exception as e:
            print(f"**Error: {e}**")

    def visualize(self):
        try:
            # Clear previous plot
            self.axes.clear()
            
            # Get file path
            file_path = self.file_path_entry.get()

           # Get sampling frequency
            sampling_freq = float(self.sampling_freq_entry.get())

            # Get start and end times as strings from entries
            start_time_str = self.start_time_hour_entry.get()+":"+self.start_time_minute_entry.get()+":"+ self.start_time_second_entry.get()
            end_time_str =self.end_time_hour_entry.get()+":"+self.end_time_minute_entry.get()+":"+self.end_time_second_entry.get()            

            # Parse start and end times into seconds
            start_time_in_seconds = self.parse_time_string(start_time_str)
            end_time_in_seconds = self.parse_time_string(end_time_str)  

            # Read EEG data from CSV file           
            with open(file_path, "r") as f:
                reader = csv.reader(f)
                timestamps = []
                eeg_data = []  # Assuming a single EEG channel
                next(reader)
                next(reader)
                c=0  #flag
                for row in reader:                
                    if eval(row[0])>=start_time_in_seconds and end_time_in_seconds>=eval(row[0]) :
                        c+=1
                        timestamps.append(eval(row[0]))  # Assuming time is in the first column
                        eeg_data.append(eval(row[1]))  # Assuming EEG data is in the second column
                    elif c>0:
                        break

            # Calculate number of data points to display based on sampling frequency and time
            start_index = int(start_time_in_seconds * sampling_freq)
            end_index = min(int(end_time_in_seconds * sampling_freq), len(timestamps)) if end_time_in_seconds else len(timestamps)
            print("v_sec: ",start_time_in_seconds,end_time_in_seconds)
            print("v: ",start_index,end_index)           
            # Plot EEG data
            self.axes.clear()
            self.axes.plot(timestamps, eeg_data)
            self.axes.set_xlabel("Time (seconds)")
            self.axes.set_ylabel("EEG Amplitude")
            self.axes.set_title("EEG Data Visualization")
            self.canvas.draw()  # Update the plot
        
            # Get comments and current date/time
            comments = self.comment_entry.get()
            current_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Save comments and date/time to CSV file
            self.save_comments_to_csv(comments, current_date_time)
        except ValueError as ve:
            print(f"**Error: {ve}**")
        except Exception as e:
            print(f"**Error: {e}**")

    def reset_graph(self):
        """
        Reset the graph by clearing all highlighted regions and resetting the plot.
        """
        self.axes.clear()
        self.highlighted_data = []  # Clear the list of highlighted regions
        self.canvas.draw()

    def parse_time_string(self, time_str):
        """
        Parses a time string in HH:MM:SS format and returns the total time in seconds.

        Args:
            time_str (str): Time string in HH:MM:SS format.

        Returns:
            float: Total time in seconds.

        Raises:
            ValueError: If the time string is not in the correct format.
        """
        try:
            hours, minutes, seconds = map(int, time_str.split(":"))
            if (hours < 0 or hours >= 24) or (minutes < 0 or minutes >= 60) or (seconds < 0 or seconds >= 60):
                raise ValueError("Invalid time values")
            return  ((hours*3600)+(minutes*60)+seconds)
           
        except ValueError:
            print("except")
            raise ValueError("Invalid time format (HH:MM:SS expected)")

# Run the GUI application
root = tk.Tk()
app = LoginPage(root)
root.mainloop()
