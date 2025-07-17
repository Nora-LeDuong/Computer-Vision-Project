# EncodeGenerator.py

import cv2
import face_recognition
import pickle
import os
import csv

# Đọc users.csv để map mã sinh viên → username
def load_code_to_username():
    mapping = {}
    if os.path.exists("users.csv"):
        with open("users.csv", newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                code = row['code']
                username = row['username']
                mapping[code] = username
    return mapping

folderPath = 'Images'
pathList = os.listdir(folderPath)
code_to_username = load_code_to_username()

imgList = []
studentIds = []

for filename in pathList:
    code = os.path.splitext(filename)[0]
    if code not in code_to_username:
        print(f"[WARNING] Không tìm thấy username cho mã: {code}")
        continue

    imgPath = os.path.join(folderPath, filename)
    img = cv2.imread(imgPath)
    if img is None:
        print(f"[ERROR] Không đọc được ảnh: {filename}")
        continue

    imgList.append(img)
    studentIds.append(code_to_username[code])

print("🔄 Đang mã hóa khuôn mặt...")
encodeList = []
for img in imgList:
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    faces = face_recognition.face_encodings(img)
    if faces:
        encodeList.append(faces[0])
    else:
        print("⚠️ Không tìm thấy khuôn mặt trong ảnh.")

with open("EncodeFile.p", "wb") as f:
    pickle.dump([encodeList, studentIds], f)

print("✅ Đã lưu vào EncodeFile.p")
