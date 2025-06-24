import tkinter as tk
from tkinter import messagebox
import cv2
import os
import csv
import face_recognition
import pickle
import numpy as np
from PIL import Image, ImageTk

root = tk.Tk()
root.title("Face Login System")
root.geometry("900x650")
root.resizable(False, False)

# === Biến toàn cục
camera_label = None
cap = None
current_frame = None
capture_button = None
encodeListKnown = []
studentIds = []

# === Tải dữ liệu đã mã hóa
if os.path.exists("EncodeFile.p"):
    with open("EncodeFile.p", "rb") as f:
        encodeListKnown, studentIds = pickle.load(f)

# === Load người dùng
def load_users():
    users = {}
    if not os.path.exists("users.csv"):
        return users
    with open("users.csv", newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            users[row['username']] = {
                'email': row['email'],
                'password': row['password']
            }
    return users

def username_exists(username): return username in load_users()
def email_exists(email): return any(u['email'] == email for u in load_users().values())

def save_user(username, email, password):
    file_exists = os.path.exists("users.csv")
    with open("users.csv", mode='a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['username', 'email', 'password'])
        if not file_exists:
            writer.writeheader()
        writer.writerow({'username': username, 'email': email, 'password': password})

# === Cập nhật camera định kỳ
def show_camera_for_register(username):
    global cap, current_frame, capture_button

    cap = cv2.VideoCapture(0)

    def update():
        global current_frame
        if cap and cap.isOpened():
            ret, frame = cap.read()
            if ret:
                current_frame = frame
                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = ImageTk.PhotoImage(Image.fromarray(img))
                camera_label.configure(image=img)
                camera_label.image = img
                root.after(30, update)

    # Hiển thị nút "Chụp ảnh"
    if capture_button:
        capture_button.destroy()

    def take_photo():
        global cap
        if current_frame is not None:
            path = os.path.join("Images", f"{username}.jpg")
            cv2.imwrite(path, current_frame)
            cap.release()
            messagebox.showinfo("Thành công", f"Ảnh đã được lưu.\nHãy chạy EncodeGenerator.py để cập nhật.")
            capture_button.destroy()

    capture_button = tk.Button(center_frame, text="📸 Chụp ảnh", font=("Arial", 14),
                               bg="white", command=take_photo)
    capture_button.pack(pady=5)

    update()

# === Giao diện
left_frame = tk.Frame(root, width=150, height=600, bg="lightgray")
left_frame.pack(side="left", fill="y")

center_frame = tk.Frame(root, width=500, height=600, bg="black")
center_frame.pack(side="left", fill="both", expand=True)

camera_label = tk.Label(center_frame, bg="black")
camera_label.pack(expand=True)

right_frame = tk.Frame(root, width=250, height=600)
right_frame.pack(side="right", fill="y")

def clear_right_frame():
    for widget in right_frame.winfo_children():
        widget.destroy()

def show_login_form():
    clear_right_frame()
    tk.Label(right_frame, text="Tên người dùng").pack(pady=5)
    entry_user = tk.Entry(right_frame)
    entry_user.pack()

    tk.Label(right_frame, text="Email").pack(pady=5)
    entry_email = tk.Entry(right_frame)
    entry_email.pack()

    tk.Label(right_frame, text="Mật khẩu").pack(pady=5)
    entry_pass = tk.Entry(right_frame, show="*")
    entry_pass.pack()

    def on_login():
        username = entry_user.get()
        email = entry_email.get()
        password = entry_pass.get()
        users = load_users()

        if username in users and users[username]["email"] == email and users[username]["password"] == password:
            messagebox.showinfo("Xác thực", "Thông tin hợp lệ. Đang kiểm tra khuôn mặt...")
            cap = cv2.VideoCapture(0)
            success = False
            while True:
                ret, frame = cap.read()
                if not ret:
                    continue
                imgS = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
                face_locations = face_recognition.face_locations(imgS)
                face_encodings = face_recognition.face_encodings(imgS, face_locations)
                for encodeFace in face_encodings:
                    matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                    face_distances = face_recognition.face_distance(encodeListKnown, encodeFace)
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index] and studentIds[best_match_index] == username:
                        messagebox.showinfo("Đăng nhập", f"Xin chào {username}, đăng nhập thành công!")
                        success = True
                        break
                if success:
                    break
                cv2.imshow("Đang xác thực khuôn mặt", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            cap.release()
            cv2.destroyAllWindows()
        else:
            messagebox.showerror("Lỗi", "Thông tin đăng nhập không đúng.")

    tk.Button(right_frame, text="Đăng nhập", command=on_login).pack(pady=10)

def show_register_form():
    clear_right_frame()
    tk.Label(right_frame, text="Tên người dùng").pack(pady=5)
    entry_user = tk.Entry(right_frame)
    entry_user.pack()

    tk.Label(right_frame, text="Email").pack(pady=5)
    entry_email = tk.Entry(right_frame)
    entry_email.pack()

    tk.Label(right_frame, text="Mật khẩu").pack(pady=5)
    entry_pass = tk.Entry(right_frame, show="*")
    entry_pass.pack()

    def on_register():
        username = entry_user.get()
        email = entry_email.get()
        password = entry_pass.get()

        if username_exists(username):
            messagebox.showerror("Lỗi", "Tên người dùng đã tồn tại.")
            return
        if email_exists(email):
            messagebox.showerror("Lỗi", "Email đã tồn tại.")
            return

        save_user(username, email, password)
        show_camera_for_register(username)

    tk.Button(right_frame, text="Đăng ký", command=on_register).pack(pady=10)

# === Nút chính
tk.Button(left_frame, text="Đăng nhập", width=18, command=show_login_form).pack(pady=10)
tk.Button(left_frame, text="Đăng ký", width=18, command=show_register_form).pack(pady=10)

root.mainloop()
