📸 Smart Face Recognition Attendance System

A desktop application that automates attendance tracking using facial recognition technology. Built with Python, OpenCV, and Tkinter, this system offers a modern GUI, real-time voice feedback, and SQLite database management.

🌟 Key Features
Real-Time Face Recognition: Identify registered users instantly via webcam.

Modern GUI: A clean, responsive interface built with Tkinter and ttk styling.

Voice Feedback: Text-to-speech integration (pyttsx3) greets users by name upon successful marking.

User Management: easy interface to Register (capture from webcam) and Deregister users.

Automated Database: Stores attendance records (Name, Date, Time) in a local SQLite database.

Data Export: One-click export of attendance logs to .csv format for Excel/Google Sheets.

Duplicate Prevention: Prevents marking the same user multiple times in a single session.

🛠️ Tech Stack
Language: Python 3

Computer Vision: face_recognition, opencv-python (cv2)

GUI: tkinter (Standard Python Library)

Database: sqlite3

Audio: pyttsx3

Image Processing: Pillow (PIL), numpy

⚙️ Installation
1. Clone the Repository
Bash

git clone https://github.com/yourusername/face-recog-attendance.git
cd face-recog-attendance
2. Install Dependencies
Note for Windows Users: The face_recognition library depends on dlib. You may need to install CMake and Visual Studio C++ Build Tools before installing the requirements.

Run the following command to install the required libraries:

Bash

pip install opencv-python numpy face_recognition pyttsx3 Pillow
Troubleshooting dlib errors? If pip install face_recognition fails, try installing a pre-compiled wheel of dlib or ensure you have CMake installed (pip install cmake).

🚀 How to Use
Run the Application:

Bash

python face_recog.py
Register a User:

Enter the person's name in the "Register New Face" section.

Click Register Face.

A window will open showing the webcam feed. Click "Capture and Register" to save the face data.

Start Attendance:

Click Start Attendance.

The webcam window will open.

When a registered face is detected, the system will draw a green box around the face, display the name, announce "Hello [Name]", and save the record to the database.

Export Data:

Click Export Attendance to CSV to save a timestamped spreadsheet of all attendance records.

Deregister:

Click Deregister Face, select a name from the dropdown, and confirm to remove their biometric data.

🧠 How It Works
Encoding: When a face is registered, the system calculates a 128-dimension face encoding vector and saves the image to the faces/ directory.

Matching: During the "Start Attendance" loop, the system processes every 5th frame (for performance optimization). It compares the live video face encodings against the known database using Euclidean distance.

Logging: If a match is found within the tolerance threshold, the name and current timestamp are logged into attendance.db.

🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

Fork the project

Create your Feature Branch (git checkout -b feature/AmazingFeature)

Commit your changes (git commit -m 'Add some AmazingFeature')

Push to the Branch (git push origin feature/AmazingFeature)

Open a Pull Request
