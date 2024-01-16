import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from cryptography.fernet import Fernet
import bcrypt

# Constants
ATTENDANCE_FILE_PATH = 'attendance.csv'
UPLOAD_FOLDER = r'C:\Users\Pc\Desktop\security\IMAGE_FILES'  # Folder for attendance faces
LOGIN_FACES_FOLDER = r'C:\Users\Pc\Desktop\security\LOGIN_FACES_IMAGES'  # Folder for login faces
PASSWORDS_FILE = 'passwords.txt'

# Key for encryption
encryption_key = Fernet.generate_key()
cipher_suite = Fernet(encryption_key)

#####################################################

class FaceRecognitionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Recognition System")

        # Window size and position
        self.root.geometry("400x300+300+300")
        self.root.resizable(False, False)  # Disable window resizing

        # Configure style
        self.style = ttk.Style()

        # Customize login page
        self.style.configure("TButton", padding=5, relief="flat", background="#40E0D0", foreground="Black")
        self.style.configure("TLabel", padding=5, background="#FFFFFF", foreground="Black", font=("Helvetica", 14))
        self.style.configure("TEntry", padding=5, background="white", foreground="#2c3e50")

        self.create_widgets()

    def create_widgets(self):
        login_frame = ttk.Frame(self.root, padding=(70, 10, 10, 10), style="TFrame")  # Adjust padding values
        login_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), columnspan=3)  # Span 3 columns for a wider frame

        # Header
        header_label = ttk.Label(login_frame, text="Admin Login", style="TLabel")
        header_label.grid(row=0, column=0, pady=5, columnspan=3)  # Span 3 columns for a wider label

        # Login for username and password
        self.label_username = ttk.Label(login_frame, text="Username:", style="TLabel", font=("Helvetica", 12))
        self.entry_username = ttk.Entry(login_frame, style="TEntry", width=20)  # Set the width of the entry field
        self.label_password = ttk.Label(login_frame, text="Password:", style="TLabel", font=("Helvetica", 12))
        self.entry_password = ttk.Entry(login_frame, style="TEntry", show="*", width=20)  # Set the width of the entry field
        self.button_login_username = ttk.Button(login_frame, text="Login with Password", command=self.login_with_username, style="TButton")
        
        # Login for Face
        self.button_login_face = ttk.Button(login_frame, text="Login with Face", command=self.login_with_face, style="TButton")
        
        # Register Face
        self.button_register_face = ttk.Button(login_frame, text="Register New Face", command=self.register_new_face, style="TButton")

        self.label_username.grid(row=1, column=0, pady=5, padx=10, columnspan=2)  # Span 2 columns for a wider label
        self.entry_username.grid(row=1, column=2, pady=5, padx=10)  # Adjust the column to 2
        self.label_password.grid(row=2, column=0, pady=5, padx=10, columnspan=2)  # Span 2 columns for a wider label
        self.entry_password.grid(row=2, column=2, pady=5, padx=10)  # Adjust the column to 2
        self.button_login_username.grid(row=3, column=0, columnspan=3, pady=10, sticky="nsew")
        self.button_login_face.grid(row=4, column=0, columnspan=3, pady=10, sticky="nsew")
        self.button_register_face.grid(row=5, column=0, columnspan=3, pady=10, sticky="nsew")

#####################################################

    def login_with_face(self):
        # Capture an image from the camera for face detection
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()

        # Convert the captured frame to RGB format
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)

        if len(face_locations) > 0:
            face_encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]

            # Known faces for login
            login_face_encodings = encoding_img([cv2.imread(os.path.join(LOGIN_FACES_FOLDER, file)) for file in os.listdir(LOGIN_FACES_FOLDER)])
            matches = face_recognition.compare_faces(login_face_encodings, face_encoding)

            if any(matches):
                # Proceed to the face recognition page
                self.show_face_recognition_page()
            else:
                # Unregistered face
                messagebox.showerror("Login Failed", "Unregistered face. Please register your face.")
        else:
            # No face detected
            messagebox.showerror("Login Failed", "No face detected. Please try again.")

#####################################################
            
    def login_with_username(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        # Check if username and password are correct
        if self.verify_password(username, password):
            self.show_face_recognition_page()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password. Please try again.")

#####################################################

    def register_new_face(self):
        # Ask for the admin password
        admin_password = simpledialog.askstring("Admin Authentication", "Enter admin password:", show='*')

        # Check if the entered admin password is correct
        if self.verify_admin_password(admin_password):
            # Capture an image from the camera for face registration
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            cap.release()

            # Convert the captured frame to RGB format
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)

            if len(face_locations) > 0:
                # Encode the detected face
                face_encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]

                # Ask the admin for a unique name for the face
                admin_name = simpledialog.askstring("Register Face", "Enter admin name for registration:")

                # Save the encoded face to the LOGIN_FACES_IMAGES folder
                file_path = os.path.join(LOGIN_FACES_FOLDER, f'{admin_name}.jpg')
                cv2.imwrite(file_path, frame)

                messagebox.showinfo("Registration Successful", "New face registered successfully.")
            else:
                # No face detected
                messagebox.showerror("Registration Failed", "No face detected. Please try again.")
        else:
            messagebox.showerror("Authentication Failed", "Incorrect admin password. Registration aborted.")

#####################################################

    def verify_admin_password(self, entered_password):
        # Read hashed admin password from the file
        admin_username = "admin"  # Assuming the admin username is "admin"
        with open(PASSWORDS_FILE, 'r') as file:
            for line in file:
                stored_username, stored_hashed_password = line.strip().split(',')
                if admin_username == stored_username:
                    # Check if the entered password matches the stored hashed password
                    return bcrypt.checkpw(entered_password.encode(), stored_hashed_password.encode())

        return False

#####################################################

    def verify_password(self, username, password):
        # Read hashed passwords from the file
        with open(PASSWORDS_FILE, 'r') as file:
            for line in file:
                stored_username, stored_hashed_password = line.strip().split(',')
                if username == stored_username:
                    # Check if the entered password matches the stored hashed password
                    return bcrypt.checkpw(password.encode(), stored_hashed_password.encode())
        return False
    
##################################################################################################################
    
    def show_face_recognition_page(self):
        self.root.destroy()  # Close the login page

        # Face Recognition Page
        face_recognition_window = tk.Tk()
        face_recognition_window.title("Face Recognition")

        # Window size and position
        face_recognition_window.geometry("800x400+200+100")
        face_recognition_window.resizable(False, False)  # Disable window resizing

        self.style.configure("TButton", padding=6, relief="flat", background="#4CAF50", foreground="white")
        self.style.configure("TLabel", padding=6, background="#2c3e50", foreground="white")
        self.style.configure("TFrame", background="#4CAF50")

        title_label = ttk.Label(face_recognition_window, text="Student Attendance", font=("Helvetica", 16), style="TLabel")
        title_label.pack(pady=10)

        # Attendance Table
        frame = ttk.Frame(face_recognition_window, style="TFrame")
        frame.pack(pady=10)

        self.attendance_table = ttk.Treeview(frame, columns=('Name', 'Time', 'Attendance'))
        self.attendance_table.heading('#0', text='Student Name')
        self.attendance_table.heading('#1', text='Time')
        self.attendance_table.heading('#2', text='Attendance')
        self.attendance_table.column('#2', stretch=tk.NO, width=80)  # Set a fixed width for the Attendance column
        self.attendance_table.pack()

        self.button_mark_attendance = ttk.Button(face_recognition_window, text="Start Scan", command=self.mark_attendance, style="TButton")
        self.button_mark_attendance.pack(pady=10)

        self.button_logout = ttk.Button(face_recognition_window, text="Logout", command=lambda: self.logout(face_recognition_window), style="TButton")
        self.button_logout.pack(pady=10)

        face_recognition_window.mainloop()

#####################################################

    def logout(self, face_recognition_window):
        face_recognition_window.destroy()  # Close the face recognition page
        new_root = tk.Tk()
        app = FaceRecognitionApp(new_root)
        new_root.mainloop()

#####################################################

    def mark_attendance(self):
        create_attendance_file()

        IMAGE_FILES = []
        filename = []
        dir_path = UPLOAD_FOLDER  # Change to the attendance image folder

        for imagess in os.listdir(dir_path):
            img_path = os.path.join(dir_path, imagess)
            img_path = face_recognition.load_image_file(img_path)
            IMAGE_FILES.append(img_path)
            filename.append(imagess.split(".", 1)[0])

        encodeListknown = encoding_img(IMAGE_FILES)
        cap = cv2.VideoCapture(0)

        while True:
            success, img = cap.read()
            imgc = cv2.resize(img, (0, 0), None, 0.25, 0.25)
            imgc = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            fasescurrent = face_recognition.face_locations(imgc)
            encode_fasescurrent = face_recognition.face_encodings(imgc, fasescurrent)

            for encodeFace, faceloc in zip(encode_fasescurrent, fasescurrent):
                matches_face = face_recognition.compare_faces(encodeListknown, encodeFace)
                face_distence = face_recognition.face_distance(encodeListknown, encodeFace)
                matchindex = np.argmin(face_distence)

                if matches_face[matchindex]:
                    name = filename[matchindex].upper()
                    y1, x2, y2, x1 = faceloc
                    cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)
                    cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (255, 0, 0), 2, cv2.FILLED)
                    cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    self.take_attendance(name)
                    self.update_attendance_table(name)
                else:
                    # Unknown
                    y1, x2, y2, x1 = faceloc
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 0, 255), 2, cv2.FILLED)
                    cv2.putText(img, "Unknown", (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            cv2.imshow('Face Recognition', img)
            key = cv2.waitKey(1)
            if key == 27:  # Press 'Esc' to exit
                break

        cap.release()
        cv2.destroyAllWindows()

#####################################################

    def take_attendance(self, name):
        now = datetime.now()
        date_string = now.strftime('%H:%M:%S')
        data_to_encrypt = f'{name},{date_string},Present'.encode()

        # Encrypt the data
        encrypted_data = cipher_suite.encrypt(data_to_encrypt)

        with open(ATTENDANCE_FILE_PATH, 'ab') as f:  # 'ab' for binary mode
            f.write(encrypted_data + b'\n')

#####################################################

    def update_attendance_table(self, name):
        now = datetime.now()
        time_string = now.strftime('%H:%M:%S')
        data_to_encrypt = f'{name},{time_string},Present'.encode()
        encrypted_data = cipher_suite.encrypt(data_to_encrypt)

        self.attendance_table.insert('', 'end', text=name, values=(time_string, 'Present'))

#####################################################

def create_attendance_file():
    if not os.path.exists(ATTENDANCE_FILE_PATH):
        with open(ATTENDANCE_FILE_PATH, 'w') as f:
            f.write('Name,Time,Attendance\n')

#####################################################

def encoding_img(IMAGE_FILES):
    encodeList = []
    for img in IMAGE_FILES:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

if __name__ == "__main__":
    root = tk.Tk()
    app = FaceRecognitionApp(root)
    root.mainloop()
