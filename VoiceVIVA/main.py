import face_recognition
import cv2
import numpy as np
import csv
from datetime import datetime
import time
import os

def get_image_file_names(folder_path):
    image_file_names = []
    # Check if the folder exists
    if os.path.exists(folder_path):
        # Iterate through all files in the folder
        for file_name in os.listdir(folder_path):
            # Check if the file is an image (you can adjust this condition based on your specific file types)
            if file_name.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                image_file_names.append(file_name)
    else:
        print("Folder doesn't exist.")
    return image_file_names


def face_recognition_func():
    # Load known face images and their encodings
    known_face_encodings = []
    known_face_names = []

    # Provide the path to the uploads folder
    uploads_folder_path = "uploads"

    # Get the image file names
    image_names = get_image_file_names(uploads_folder_path)

    # Print the image file names
    print("Image file names in the 'uploads' folder:")
    for name in image_names:
        print(name)
        name2 = name.split('.')[0]
        name2 = name2.replace("_"," ")
        print(name2)
        image = face_recognition.load_image_file(f"uploads/{name}")
        encoding = face_recognition.face_encodings(image)[0]
        known_face_encodings.append(encoding)
        known_face_names.append(name2)


    students = known_face_names.copy()

    # Open video capture
    video_capture = cv2.VideoCapture(0)

    # Open CSV file for writing attendance
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    csv_filename = current_date + '.csv'
    csv_file = open(csv_filename, 'w+', newline='')
    csv_writer = csv.writer(csv_file)

    # Define variables for face recognition frequency
    FRAME_SKIP = 5  # Perform face recognition every 5 frames
    frame_count = 0
    face_locations = []
    face_names = []

    start_time = time.time()  # Get current time
    
    while True:
        # Capture frame-by-frame
        ret, frame = video_capture.read()
        
        # Increment frame count
        frame_count += 1
        
        # Resize frame to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert BGR color (used by OpenCV) to RGB color (used by face_recognition)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        # Perform face recognition every few frames
        if frame_count % FRAME_SKIP == 0:
            # Find all face locations and encodings in the current frame
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:
                # Check if the face matches any known face
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"

                # If a match is found, use the name of the known face
                if True in matches:
                    first_match_index = matches.index(True)
                    name = known_face_names[first_match_index]

                    # If the recognized face is a student, mark attendance
                    if name in students:
                        students.remove(name)
                        current_time = now.strftime("%H-%M-%S")
                        csv_writer.writerow([name, current_time])

                face_names.append(name)
        else:
            # Use previously detected face names
            pass

            # Display the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with the name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        # Display the resulting image
        cv2.imshow('Video', frame)

        # Check for the 'q' key to exit the loop
        if cv2.waitKey(1) & 0xFF == ord('q') or time.time() - start_time >= 20:
            break
 
    csv_file.close()
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    name = ""
    # Form the CSV filename
    csv_filename = current_date + '.csv'
    
    # Open the CSV file for reading
    with open(csv_filename, 'r', newline='') as csv_file:
        csv_reader = csv.reader(csv_file)
        
        # Iterate over each row in the CSV file
        for row in csv_reader:
            # Process each row as needed
            if row:  # Check if the row is not empty
                name = row[0].split(',')[0]  # Split by comma and take the first part
                print(name)   
      
    # Release video capture and close CSV file
    video_capture.release()
    cv2.destroyAllWindows()
    csv_file.close()
    if(name != None):
        return name
    else:
        return "unkown"

# # If you want to test the function, you can call it like this:
# face_recognition_func()
