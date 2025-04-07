import os
import random
import shutil

# ตั้งค่า paths (แก้ไข path ให้ถูกต้อง)
dataset_path = r"D:\yolov8\datasets"
train_images_path = os.path.join(dataset_path, "train", "images")
train_labels_path = os.path.join(dataset_path, "train", "labels")
valid_images_path = os.path.join(dataset_path, "valid", "images")
valid_labels_path = os.path.join(dataset_path, "valid", "labels")

# สร้างโฟลเดอร์ valid ถ้ายังไม่มี
os.makedirs(valid_images_path, exist_ok=True)
os.makedirs(valid_labels_path, exist_ok=True)

# ดึงรายการไฟล์ทั้งหมดจาก train/images
image_files = [f for f in os.listdir(train_images_path) if f.endswith(".jpg")]

# คำนวณจำนวนไฟล์ที่ต้องย้าย (20% ของ train)
num_valid = int(len(image_files) * 0.2)

# สุ่มเลือกไฟล์
valid_images = random.sample(image_files, num_valid)

# ย้ายไฟล์ไป valid/
for image_file in valid_images:
    label_file = image_file.replace(".jpg", ".txt")  # ไฟล์ labels ที่ตรงกับภาพ

    # ย้ายภาพไป valid/images/
    shutil.move(os.path.join(train_images_path, image_file), os.path.join(valid_images_path, image_file))
    
    # ย้าย labels ไป valid/labels/ (ถ้ามี)
    if os.path.exists(os.path.join(train_labels_path, label_file)):
        shutil.move(os.path.join(train_labels_path, label_file), os.path.join(valid_labels_path, label_file))
