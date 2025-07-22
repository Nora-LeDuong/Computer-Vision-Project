from ultralytics import YOLO
import tkinter as tk
from tkinter import messagebox
import cv2, os, csv, time, pickle
import numpy as np
from PIL import Image, ImageTk
import face_recognition

# Load mô hình YOLOv8 để phát hiện khuôn mặt
yolo_model = YOLO("yolov8n.pt") 

#Tạo cửa sổ chính giao diện
root = tk.Tk()
root.title("Face Login System")
root.geometry("900x650")
root.resizable(False, False)

#Khai báo biến toàn cục
camera_label = None
cap = None
current_frame = None
capture_button = None
encodeListKnown, studentIds = [], []

#Nếu đã có file EncodeFile.p thì tải lên danh sách mã hóa khuôn mặt
if os.path.exists("EncodeFile.p"):
    with open("EncodeFile.p", "rb") as f:
        encodeListKnown, studentIds = pickle.load(f)

#Đọc thông tin người dùng từ file users.csv
def load_users():
    users = {}
    if not os.path.exists("users.csv"): return users
    with open("users.csv", newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            users[row['username']] = {
                'email': row['email'],
                'password': row['password'],
                'code': row.get('code', '')
            }
    return users

#Hàm kiểm tra trùng tên, email, mã sinh viên
def username_exists(u): return u in load_users()
def email_exists(e): return any(u['email'] == e for u in load_users().values())
def student_code_exists(c): return any(u['code'] == c for u in load_users().values())

#Lưu thông tin người dùng mới vào file users.csv
def save_user(username, email, password, code):
    file_exists = os.path.exists("users.csv")
    with open("users.csv", mode='a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['username', 'email', 'password', 'code'])
        if not file_exists: writer.writeheader()
        writer.writerow({'username': username, 'email': email, 'password': password, 'code': code})

#Kiểm tra khuôn mặt đã đươc đăng ký hay chưa
def is_face_already_registered(new_face_encoding):
    for file in os.listdir("Images"):
        img = cv2.imread(os.path.join("Images", file))
        if img is None: continue
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodes = face_recognition.face_encodings(rgb)
        if encodes and face_recognition.compare_faces([encodes[0]], new_face_encoding)[0]:
            return True
    return False

#Mở camera để chụp ảnh đăng ký khuôn mặt
def show_camera_for_register(username, code):
    global cap, current_frame, capture_button
    cap = cv2.VideoCapture(0)
    cap.set(3, 640); cap.set(4, 480)

    def update():
        global current_frame
        if cap and cap.isOpened():
            ret, frame = cap.read()
            if ret:
                current_frame = frame
                img = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
                camera_label.configure(image=img)
                camera_label.image = img
                root.after(30, update)

    #Hàm chụp ảnh và lưu ảnh vào Images
    def take_photo():
        global cap
        if current_frame is not None:
            encodings = face_recognition.face_encodings(cv2.cvtColor(current_frame, cv2.COLOR_BGR2RGB))
            if not encodings:
                messagebox.showerror("Lỗi", "Không nhận diện được khuôn mặt.")
                return
            if is_face_already_registered(encodings[0]):
                messagebox.showerror("Lỗi", "Khuôn mặt này đã được đăng ký.")
                return
            path = os.path.join("Images", f"{code}.jpg")
            cv2.imwrite(path, current_frame)
            cap.release()
            camera_label.config(image='', bg='black')
            messagebox.showinfo("Thành công", f"Đã lưu ảnh. Hãy chạy EncodeGenerator.py để cập nhật.")
            capture_button.destroy()

    #Hàm hiển thị nút chụp ảnh
    capture_button = tk.Button(center_frame, text="📸 Chụp ảnh", font=("Arial", 14), bg="white", command=take_photo)
    capture_button.pack(pady=5)
    update()

#Tạo GUI
left_frame = tk.Frame(root, width=150, bg="lightgray"); left_frame.pack(side="left", fill="y")
center_frame = tk.Frame(root, width=500, bg="black"); center_frame.pack(side="left", fill="both", expand=True)
camera_label = tk.Label(center_frame, bg="black"); camera_label.pack(expand=True)
right_frame = tk.Frame(root, width=250); right_frame.pack(side="right", fill="y")

def clear_right_frame(): [w.destroy() for w in right_frame.winfo_children()]

#Giao diện đăng nhập
def show_login_form():
    clear_right_frame()
    tk.Label(right_frame, text="Email").pack(pady=5)
    email_entry = tk.Entry(right_frame); email_entry.pack()
    tk.Label(right_frame, text="Mật khẩu").pack(pady=5)
    pass_entry = tk.Entry(right_frame, show="*"); pass_entry.pack()

    #Hàm chạy lỗi khi bấm đăng nhập
    def on_login():
        email, password = email_entry.get(), pass_entry.get()
        users = load_users()
        username = next((u for u, info in users.items() if info['email'] == email), None)
        if not username or users[username]["password"] != password:
            messagebox.showerror("Lỗi", "Email hoặc mật khẩu sai.")
            return

        messagebox.showinfo("Xác thực", "Mở camera xác thực khuôn mặt...")
        global cap
        cap = cv2.VideoCapture(0)
        cap.set(3, 640); cap.set(4, 480)
        start_time = time.time()

        #Hàm kiểm tra khuôn mặt
        def verify_face_loop():
            ret, frame = cap.read()
            if not ret:
                root.after(30, verify_face_loop)
                return
            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img_tk = ImageTk.PhotoImage(Image.fromarray(img_rgb))
            camera_label.configure(image=img_tk)
            camera_label.image = img_tk

            if time.time() - start_time < 2.5:
                root.after(30, verify_face_loop)
                return

            #Dự đoán khuôn mặt bằng YOLO
            results = yolo_model.predict(frame, verbose=False)[0]
            for box in results.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                face_crop = frame[y1:y2, x1:x2]
                face_enc = face_recognition.face_encodings(cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB))
                if face_enc:
                    matches = face_recognition.compare_faces(encodeListKnown, face_enc[0])
                    face_distances = face_recognition.face_distance(encodeListKnown, face_enc[0])
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        if studentIds[best_match_index] == username:
                            messagebox.showinfo("✅ Thành công", f"Đăng nhập thành công, xin chào {username} ✔️")
                            cap.release()
                            camera_label.config(image='', bg='black')
                            return
                        else:
                            messagebox.showerror("❌ Thất bại",
                                                 "Khuôn mặt không trùng khớp với tài khoản. Đăng nhập thất bại ❌")
                            cap.release()
                            camera_label.config(image='', bg='black')
                            return

            root.after(30, verify_face_loop)

        verify_face_loop()

    tk.Button(right_frame, text="Đăng nhập", command=on_login).pack(pady=10)

#Giao diện đăng ký
def show_register_form():
    clear_right_frame()
    tk.Label(right_frame, text="Tên người dùng").pack(pady=5)
    entry_user = tk.Entry(right_frame); entry_user.pack()
    tk.Label(right_frame, text="Email").pack(pady=5)
    entry_email = tk.Entry(right_frame); entry_email.pack()
    tk.Label(right_frame, text="Mật khẩu").pack(pady=5)
    entry_pass = tk.Entry(right_frame, show="*"); entry_pass.pack()
    tk.Label(right_frame, text="Mã sinh viên").pack(pady=5)
    entry_code = tk.Entry(right_frame); entry_code.pack()

    #Hàm chạy lỗi khi bấm đăng ký
    def on_register():
        u, e, p, c = entry_user.get(), entry_email.get(), entry_pass.get(), entry_code.get()
        if not c.startswith("2301") or len(c) != 8 or not c.isdigit():
            messagebox.showerror("Lỗi", "Mã sinh viên không hợp lệ.")
            return
        if student_code_exists(c) or username_exists(u) or email_exists(e):
            messagebox.showerror("Lỗi", "Tên, email hoặc mã sinh viên đã tồn tại.")
            return
        save_user(u, e, p, c)
        show_camera_for_register(u, c)

    tk.Button(right_frame, text="Đăng ký", command=on_register).pack(pady=10)

#Nút chọn đăng nhập, đăng ký
tk.Button(left_frame, text="Đăng nhập", width=18, command=show_login_form).pack(pady=10)
tk.Button(left_frame, text="Đăng ký", width=18, command=show_register_form).pack(pady=10)

root.mainloop()
