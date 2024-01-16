#Face unknown plus GUI
import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import simpledialog
from PIL import Image, ImageTk

UPLOAD_FOLDER = r'C:\Users\Pc\Desktop\security\IMAGE_FILES'
ATTENDANCE_FILE_PATH = 'attendance.csv'

def create_attendance_file():
    if not os.path.exists(ATTENDANCE_FILE_PATH):
        with open(ATTENDANCE_FILE_PATH, 'w') as f:
            f.write('Name,Time\n')

def take_attendance(name):
    with open(ATTENDANCE_FILE_PATH, 'a') as f:
        now = datetime.now()
        date_string = now.strftime('%H:%M:%S')
        f.write(f'{name},{date_string}\n')

def encoding_img(IMAGE_FILES):
    encodeList = []
    for img in IMAGE_FILES:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

def login(name):
    print(f"Logged in as: {name}")

def recognize_user(username, encodeListknown):
    if username in encodeListknown:
        return True
    else:
        return False

def main():
    def stop_face_recognition():
        nonlocal face_recognition_running, cap
        face_recognition_running = False
        cap.release()
        cv2.destroyAllWindows()  # Close the OpenCV window

        # Enable the login button and disable the stop button
        stop_button.config(state=tk.DISABLED)
        login_button.config(state=tk.NORMAL)

    create_attendance_file()

    IMAGE_FILES = []
    filename = []
    dir_path = r'C:\Users\Pc\Desktop\security\IMAGE_FILES'

    for imagess in os.listdir(dir_path):
        img_path = os.path.join(dir_path, imagess)
        img_path = face_recognition.load_image_file(img_path)
        IMAGE_FILES.append(img_path)
        filename.append(imagess.split(".", 1)[0])

    encodeListknown = encoding_img(IMAGE_FILES)
    cap = cv2.VideoCapture(0)

    root = tk.Tk()
    root.title("Face Recognition Login")
    root.geometry("640x720")

    label = tk.Label(root, text="Enter your username:")
    label.pack(pady=10)

    entry = tk.Entry(root)
    entry.pack(pady=10)

    login_button = tk.Button(root, text="Login", command=lambda: login_action(entry.get(), encodeListknown))
    login_button.pack(pady=10)

    stop_button = tk.Button(root, text="Stop", command=stop_face_recognition)
    stop_button.pack(pady=10)
    stop_button.config(state=tk.DISABLED)  # Initially disable the stop button

    canvas = tk.Canvas(root, width=640, height=480)
    canvas.pack()

    last_attendance = {}  # Dictionary to store the last attendance timestamp for each user
    face_recognition_running = False

    def login_action(username, encodeListknown):
        nonlocal face_recognition_running, cap
        face_recognition_running = not face_recognition_running

        if face_recognition_running:
            if not username:
                print("Username not entered.")
                return

            if recognize_user(username, filename):
                print("User recognized. Starting face recognition...")
                # Release the existing capture before creating a new one
                cap.release()
                cap = cv2.VideoCapture(0)
                perform_face_recognition(username, encodeListknown)
            else:
                print("Unknown user. Please try again.")
        else:
            stop_face_recognition()

    def perform_face_recognition(username, encodeListknown):
        nonlocal last_attendance, cap

        stop_button.config(state=tk.NORMAL)  # Enable the stop button
        login_button.config(state=tk.DISABLED)  # Disable the login button while face recognition is running

        while face_recognition_running:
            success, img = cap.read()

            if not success:
                print("Failed to read the frame.")
                break

            imgc = cv2.resize(img, (0, 0), None, 0.25, 0.25)
            imgc = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            fasescurrent = face_recognition.face_locations(imgc)
            encode_fasescurrent = face_recognition.face_encodings(imgc, fasescurrent)

            for encodeFace, faceloc in zip(encode_fasescurrent, fasescurrent):
                matches_face = face_recognition.compare_faces(encodeListknown, encodeFace, tolerance=0.5)

                y1, x2, y2, x1 = faceloc
                if True in matches_face:
                    matchindex = matches_face.index(True)
                    name = filename[matchindex].upper()

                    # Check if the user has already been marked present in the last 24 hours
                    if name in last_attendance:
                        last_attendance_time = last_attendance[name]
                        time_difference = datetime.now() - last_attendance_time

                        if time_difference < timedelta(days=1):
                            print(f"{name} is already marked present. Please try again later.")
                            continue

                    cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)
                    cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (255, 0, 0), 2, cv2.FILLED)
                    cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

                    take_attendance(name)
                    last_attendance[name] = datetime.now()  # Update the last attendance timestamp
                    login(name)  # Add login function call here

                else:
                    # Draw a rectangle around the face and label it as "Unknown"
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 0, 255), 2, cv2.FILLED)
                    cv2.putText(img, "Unknown", (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, (640, 480))

            tk_img = ImageTk.PhotoImage(Image.fromarray(img))
            canvas.create_image(0, 0, anchor=tk.NW, image=tk_img)
            canvas.image = tk_img

            root.update()

            key = cv2.waitKey(1)
            if key == 27:  # Press 'Esc' to exit
                break

        stop_face_recognition()

    root.mainloop()

if __name__ == "__main__":
    main()
