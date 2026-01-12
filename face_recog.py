import face_recognition
import cv2
import numpy as np
import os
import sqlite3
import pyttsx3
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import csv


# Voice Engine Setup

engine = pyttsx3.init()
engine.setProperty('rate', 160)

def speak(text):
    engine.say(text)
    engine.runAndWait()


# SQLite Setup

def init_db():
    conn = sqlite3.connect("attendance.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            date TEXT,
            time TEXT
        )
    """)
    conn.commit()
    conn.close()

def mark_attendance(name):
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")
    conn = sqlite3.connect("attendance.db")
    c = conn.cursor()
    c.execute("INSERT INTO attendance (name, date, time) VALUES (?, ?, ?)", (name, date, time))
    conn.commit()
    conn.close()


# Load Known Faces

def load_known_faces():
    known_encodings = []
    known_names = []

    for file in os.listdir("faces"):
        if file.endswith(".jpg") or file.endswith(".png"):
            path = os.path.join("faces", file)
            img = face_recognition.load_image_file(path)
            encodings = face_recognition.face_encodings(img)
            if encodings:
                known_encodings.append(encodings[0])
                known_names.append(os.path.splitext(file)[0])
            else:
                print(f"Warning: No face found in {file}")
    return known_encodings, known_names


# Attendance with Voice + DB

def start_attendance():
    known_encodings, known_names = load_known_faces()
    students = known_names.copy()

    if not known_encodings:
        messagebox.showwarning("No Faces", "Please register faces first.")
        return

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        messagebox.showerror("Webcam Error", "Cannot open webcam.")
        return
        
    messagebox.showinfo("Info", "The attendance window is now active. Close the window to stop.")

    # Create a new Tkinter window for the video feed
    video_window = tk.Toplevel(root)
    video_window.title("Live Attendance Feed")
    video_window.geometry("800x600")

    video_label = tk.Label(video_window)
    video_label.pack()

    # 1. Process only every Nth frame
    PROCESS_EVERY_N_FRAMES = 5 
    frame_count = 0

    # 2. Store last known locations and names to use on skipped frames
    face_locations = []
    face_names = []
    
    def update_frame():
        nonlocal frame_count, face_locations, face_names # Use nonlocal to modify these variables

        ret, frame = cap.read()
        if not ret:
            # Handle the case where the camera is disconnected
            on_video_window_close()
            return
            
        frame_count += 1
        
        process_this_frame = (frame_count % PROCESS_EVERY_N_FRAMES == 0)

        if process_this_frame:
            
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            
            current_face_locations = face_recognition.face_locations(rgb_frame)
            current_face_encodings = face_recognition.face_encodings(rgb_frame, current_face_locations)
            
            face_names = [] 
            for face_encoding in current_face_encodings:
                matches = face_recognition.compare_faces(known_encodings, face_encoding)
                name = "Unknown"

                face_distances = face_recognition.face_distance(known_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)

                if matches[best_match_index]:
                    name = known_names[best_match_index]

                    if name in students:
                        students.remove(name)
                        mark_attendance(name)
                        print(f"Marked attendance for {name}") 
                        speak(f"Hello {name}, your attendance is marked")
                
                face_names.append(name)

            
            face_locations = current_face_locations

        
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

            
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        imgtk = ImageTk.PhotoImage(image=img)
        video_label.imgtk = imgtk
        video_label.config(image=imgtk)

        
        video_label.after(10, update_frame)

    def on_video_window_close():
        cap.release()
        cv2.destroyAllWindows()
        video_window.destroy()
        print("Attendance stopped and window closed.")

    video_window.protocol("WM_DELETE_WINDOW", on_video_window_close)
    update_frame()



# Face Registration

def register_face():
    name = name_entry.get().strip()
    if not name:
        messagebox.showwarning("Input Error", "Please enter a name.")
        return

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        messagebox.showerror("Webcam Error", "Cannot open webcam.")
        return

    
    register_window = tk.Toplevel(root)
    register_window.title(f"Registering: {name}")
    register_window.geometry("800x650") 
    register_window.grab_set() 

    register_label = tk.Label(register_window)
    register_label.pack(pady=10)


    def capture_and_save():
        
        ret, frame = cap.read()
        if ret:
            
            os.makedirs("faces", exist_ok=True)
            
            face_path = os.path.join("faces", f"{name}.jpg")
            
            
            cv2.imwrite(face_path, frame)
            
            messagebox.showinfo("Saved", f"Face registered successfully for {name}.", parent=register_window)
            
            
            on_register_window_close()
        else:
            messagebox.showerror("Capture Error", "Could not read frame from camera.", parent=register_window)

    
    capture_button = ttk.Button(
        register_window, 
        text="Capture and Register Face", 
        command=capture_and_save, 
        style="Success.TButton"
    )
    capture_button.pack(pady=10, padx=20, fill="x")

    def update_register_frame():
        ret, frame = cap.read()
        if not ret:
            on_register_window_close()
            return
            
        
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        imgtk = ImageTk.PhotoImage(image=img)
        register_label.imgtk = imgtk
        register_label.config(image=imgtk)

        
        register_window.after(10, update_register_frame)

    def on_register_window_close():
        cap.release()
        cv2.destroyAllWindows()
        register_window.destroy()

    register_window.protocol("WM_DELETE_WINDOW", on_register_window_close)
    update_register_frame()



# Deregister Face

def deregister_face():
    faces_dir = "faces"
    if not os.path.exists(faces_dir):
        os.makedirs(faces_dir)

    names = [os.path.splitext(f)[0] for f in os.listdir(faces_dir) if f.endswith(('.jpg', '.png'))]

    if not names:
        messagebox.showinfo("No Faces", "No registered faces to delete.")
        return

    win = tk.Toplevel()
    win.title("Deregister Face")
    win.geometry("350x250")
    win.resizable(False, False)
    win.grab_set() 

    style = ttk.Style()
    style.configure("TLabel", font=("Segoe UI", 12))
    style.configure("TButton", font=("Segoe UI", 11), padding=8)
    style.configure("TCombobox", font=("Segoe UI", 11), padding=5)

    frame = ttk.Frame(win, padding="20 20 20 20")
    frame.pack(expand=True, fill="both")

    ttk.Label(frame, text="Select a face to remove:", style="TLabel").pack(pady=10)
    selected_name = tk.StringVar()
    combo = ttk.Combobox(frame, textvariable=selected_name, values=names, style="TCombobox")
    combo.pack(pady=10, fill="x", padx=20)
    combo.set("Select a name...") 

    def delete_selected():
        name = selected_name.get()
        if not name or name == "Select a name...":
            messagebox.showwarning("Select Name", "Please select a name to delete.")
            return

        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete face data for '{name}'?"):
            img_path_jpg = os.path.join(faces_dir, name + ".jpg")
            img_path_png = os.path.join(faces_dir, name + ".png")
            deleted = False

            for img_path in [img_path_jpg, img_path_png]:
                if os.path.exists(img_path):
                    os.remove(img_path)
                    deleted = True

            if deleted:
                messagebox.showinfo("Deleted", f"Face data for '{name}' removed.")
                win.destroy()
            else:
                messagebox.showerror("Error", "Face file not found.")
        else:
            messagebox.showinfo("Cancelled", "Deletion cancelled.")

    ttk.Button(frame, text="Delete Selected Face", command=delete_selected, style="Danger.TButton").pack(pady=20)
    style.configure("Danger.TButton", background="#dc3545", foreground="white", font=("Segoe UI", 11, "bold"))
    style.map("Danger.TButton",
              background=[('active', '#c82333')])


# Export Attendance to CSV

def export_attendance():
    conn = sqlite3.connect("attendance.db")
    c = conn.cursor()
    c.execute("SELECT name, date, time FROM attendance")
    rows = c.fetchall()
    conn.close()

    if not rows:
        messagebox.showinfo("No Data", "No attendance records to export.")
        return

    filename = f"attendance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    try:
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Date", "Time"])
            writer.writerows(rows)
        messagebox.showinfo("Exported", f"Attendance exported successfully to {filename}")
    except IOError as e:
        messagebox.showerror("Export Error", f"Could not export attendance: {e}")


# GUI

def build_gui():
    global root, name_entry
    root = tk.Tk()
    root.title("Advanced Face Recognition Attendance System")
    root.geometry("600x650")
    root.resizable(False, False)
    root.config(bg="#f0f2f5") 

   
    style = ttk.Style()
    style.theme_use('clam') 
    style.configure("TFrame", background="#f0f2f5")
    style.configure("TLabel", font=("Segoe UI", 14), background="#f0f2f5", foreground="#333333")
    style.configure("TButton", font=("Segoe UI", 12, "bold"), padding=12, borderwidth=0, relief="flat")
    style.configure("TEntry", font=("Segoe UI", 13), padding=8)

   
    style.map("Primary.TButton",
              background=[('active', '#0056b3')],
              foreground=[('active', 'white')],
              bordercolor=[('active', '#0056b3')])
    style.map("Success.TButton",
              background=[('active', '#218838')],
              foreground=[('active', 'white')],
              bordercolor=[('active', '#218838')])
    style.map("Warning.TButton",
              background=[('active', '#e0a800')],
              foreground=[('active', 'white')],
              bordercolor=[('active', '#e0a800')])
    style.map("Info.TButton",
              background=[('active', '#138496')],
              foreground=[('active', 'white')],
              bordercolor=[('active', '#138496')])


    # --- Main Frame ---
    main_frame = ttk.Frame(root, padding="30 30 30 30")
    main_frame.pack(expand=True, fill="both")

    # --- Title ---
    title_label = ttk.Label(main_frame, text="Attendance System", font=("Segoe UI", 24, "bold"), foreground="#007bff")
    title_label.pack(pady=(0, 30))

    # --- Face Registration Section ---
    registration_frame = ttk.LabelFrame(main_frame, text="Register New Face", padding="20 15 20 15")
    registration_frame.pack(pady=20, fill="x", padx=20)
    style.configure("TLabelFrame", font=("Segoe UI", 12, "bold"), background="#ffffff", foreground="#333333")
    style.configure("TLabelframe.Label", background="#ffffff") # Set background for the label part of LabelFrame

    ttk.Label(registration_frame, text="Enter Name:", style="TLabel").pack(pady=(0, 5), anchor="w")
    name_entry = ttk.Entry(registration_frame, style="TEntry")
    name_entry.pack(pady=(0, 15), fill="x", ipady=2) # ipady adds internal vertical padding

    register_button = ttk.Button(registration_frame, text="Register Face", command=register_face,
                                 style="Success.TButton", cursor="hand2")
    register_button.pack(pady=10, fill="x")
    style.configure("Success.TButton", background="#28a745", foreground="white")


    # --- Main Actions Section ---
    actions_frame = ttk.LabelFrame(main_frame, text="System Actions", padding="20 15 20 15")
    actions_frame.pack(pady=20, fill="x", padx=20)
    style.configure("TLabelFrame", font=("Segoe UI", 12, "bold"), background="#ffffff", foreground="#333333")
    style.configure("TLabelframe.Label", background="#ffffff") # Set background for the label part of LabelFrame

    start_button = ttk.Button(actions_frame, text="Start Attendance", command=start_attendance,
                              style="Primary.TButton", cursor="hand2")
    start_button.pack(pady=10, fill="x")
    style.configure("Primary.TButton", background="#007bff", foreground="white")

    deregister_button = ttk.Button(actions_frame, text="Deregister Face", command=deregister_face,
                                   style="Warning.TButton", cursor="hand2")
    deregister_button.pack(pady=10, fill="x")
    style.configure("Warning.TButton", background="#ffc107", foreground="#343a40")

    export_button = ttk.Button(actions_frame, text="Export Attendance to CSV", command=export_attendance,
                               style="Info.TButton", cursor="hand2")
    export_button.pack(pady=10, fill="x")
    style.configure("Info.TButton", background="#17a2b8", foreground="white")

    # --- Footer ---
    footer_label = ttk.Label(main_frame, text="© 2025 Face Recognition Attendance", font=("Segoe UI", 9),
                             foreground="#6c757d", background="#f0f2f5")
    footer_label.pack(pady=20)


    root.mainloop()

if __name__ == "__main__":
    os.makedirs("faces", exist_ok=True)
    init_db()
    build_gui()