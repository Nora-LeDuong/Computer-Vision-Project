import cv2
import face_recognition
import pickle
import os
import csv

# Thư mục chứa ảnh khuôn mặt
folderPath = 'Images'
pathList = os.listdir(folderPath)
print("[INFO] Danh sách ảnh trong thư mục:", pathList)

# Đọc danh sách người dùng hợp lệ từ users.csv
valid_usernames = []
if os.path.exists('users.csv'):
    with open('users.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            valid_usernames.append(row['username'])

print("[INFO] Người dùng hợp lệ từ users.csv:", valid_usernames)

# Lưu ảnh và tên hợp lệ
imgList = []
studentIds = []

for filename in pathList:
    name = os.path.splitext(filename)[0]
    if name not in valid_usernames:
        print(f"[WARNING] Bỏ qua ảnh không hợp lệ: {filename}")
        continue

    imgPath = os.path.join(folderPath, filename)
    img = cv2.imread(imgPath)
    if img is None:
        print(f"[ERROR] Không thể đọc ảnh: {filename}")
        continue

    imgList.append(img)
    studentIds.append(name)

print("[INFO] Bắt đầu mã hóa khuôn mặt cho các user:", studentIds)

def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        faces = face_recognition.face_encodings(img)
        if faces:
            encodeList.append(faces[0])
        else:
            print("[WARNING] Không tìm thấy khuôn mặt trong ảnh.")
    return encodeList

print("🔄 Đang mã hóa khuôn mặt ...")
encodeListKnown = findEncodings(imgList)
encodeListWithIds = [encodeListKnown, studentIds]
print("✅ Mã hóa hoàn tất")

# Lưu vào file
with open("EncodeFile.p", "wb") as f:
    pickle.dump(encodeListWithIds, f)

print("💾 Đã lưu vào EncodeFile.p")
