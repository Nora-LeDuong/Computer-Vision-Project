# 🎯 Computer Vision Project

[![GitHub Repo](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)](https://github.com/Nora-LeDuong/Computer-Vision-Project)

## 🚀 Giới thiệu
Dự án nhận diện khuôn mặt sử dụng Python, xác thực người dùng qua hai bước: tài khoản và Face ID.

---

## 🛠️ Hướng dẫn sử dụng

### 1. Clone dự án
```bash
git clone https://github.com/Nora-LeDuong/Computer-Vision-Project.git
cd Computer-Vision-Project
```

### 2. Chạy chương trình chính
```bash
python main.py
```

### 3. Đăng ký tài khoản
- Giao diện sẽ hiển thị **2 nút**: `Đăng nhập` và `Đăng ký`.
- Chọn **Đăng ký** và nhập thông tin:
  - **Tên**
  - **Gmail**
  - **Mật khẩu**
  - **Mã sinh viên**
- Sau khi đăng ký, camera sẽ mở ra. Nhấn **Chụp ảnh** để lưu khuôn mặt.

### 4. Mã hóa ảnh khuôn mặt
- Sau khi chụp ảnh thành công, chạy:
```bash
python EncodeGenarator.py
```
- Thông báo thành công sẽ xuất hiện khi mã hóa hoàn tất.

### 5. Đăng nhập & xác thực Face ID
- Đăng nhập bằng thông tin đã đăng ký.
- Camera sẽ mở để xác thực khuôn mặt (**2 bước xác thực**).
- Nếu đúng, sẽ có thông báo **Đăng nhập thành công**.
- Nếu sai, sẽ có thông báo **Sai Face ID**.

---

## 📁 Cấu trúc dự án

Computer-Vision-Project/

│

├── main.py # Chương trình chính (giao diện, đăng nhập/đăng ký)

├── EncodeGenarator.py # Mã hóa ảnh khuôn mặt

├── users.csv # Lưu thông tin người dùng

└── README.md # Hướng dẫn sử dụng


---

## 💡 Ghi chú
- Đảm bảo máy tính có camera và đã cài đặt đầy đủ các thư viện cần thiết (OpenCV, v.v).
- Nếu gặp lỗi, kiểm tra lại các bước hoặc liên hệ người phát triển.

---

## 👨‍💻 Người phát triển
- [Tên của bạn]
- [Email hoặc thông tin liên hệ]

---

**Link repository:** [https://github.com/Nora-LeDuong/Computer-Vision-Project](https://github.com/Nora-LeDuong/Computer-Vision-Project)


