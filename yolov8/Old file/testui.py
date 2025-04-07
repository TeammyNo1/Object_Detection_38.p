import tkinter as tk
from PIL import Image, ImageTk
import os
import cv2
from ultralytics import YOLO  
from tkinter import messagebox

# ตั้งค่า path ของรูปภาพปุ่มและโลโก้
assets_path = r"D:\yolov8\assets"
logo_path = os.path.join(assets_path, "BOSCH_LOGO.png")

# เริ่มต้นหน้าต่างหลัก
root = tk.Tk()
root.title("P38 Counting UI")
root.geometry("1280x720")  # ขนาดหน้าจอใหญ่ขึ้น
root.configure(bg="white")

# โหลดโลโก้และปรับขนาด
logo_img = Image.open(logo_path).resize((250, 80))
logo_photo = ImageTk.PhotoImage(logo_img)

# สร้าง Layout หลัก (แบ่งเป็น 2 ส่วน ซ้าย = UI, ขวา = กล้อง OpenCV)
main_frame = tk.Frame(root, bg="white")
main_frame.pack(side=tk.LEFT, padx=20, pady=20, anchor="nw")

# แสดงโลโก้ **เหนือ P38**
logo_label = tk.Label(main_frame, image=logo_photo, bg="white")
logo_label.pack(anchor="w", pady=5)

# ตัวแปรแสดงข้อมูล
p38_var = tk.StringVar(value="0")
p38_total_var = tk.StringVar(value="0/170")
pc_total_var = tk.StringVar(value="1/6")
box_count_var = tk.StringVar(value="0")
status_var = tk.StringVar(value="Ready")

# ฟังก์ชันสร้างช่องป้อนค่าพร้อม Label
def create_entry(parent, label_text, text_var, row):
    tk.Label(parent, text=label_text, font=("Arial", 14, "bold"), bg="white").grid(row=row, column=0, sticky="w", padx=10, pady=2)
    entry = tk.Entry(parent, textvariable=text_var, font=("Arial", 14), state="readonly", width=20, relief="solid")
    entry.grid(row=row+1, column=0, padx=10, pady=5, sticky="we")

# สร้างฟอร์มแสดงข้อมูล
form_frame = tk.Frame(main_frame, bg="white")
form_frame.pack(anchor="w", pady=10)

create_entry(form_frame, "P38", p38_var, row=0)
create_entry(form_frame, "P38 Total / Box", p38_total_var, row=2)
create_entry(form_frame, "Pc Total", pc_total_var, row=4)
create_entry(form_frame, "Box Count", box_count_var, row=6)

# ช่องแสดงสถานะ
tk.Label(form_frame, text="Status", font=("Arial", 14, "bold"), bg="white").grid(row=8, column=0, sticky="w", padx=10, pady=5)
status_entry = tk.Entry(form_frame, textvariable=status_var, font=("Arial", 14), state="readonly", width=20, relief="solid", fg="blue")
status_entry.grid(row=9, column=0, padx=10, pady=5, sticky="we")

# โหลดรูปภาพปุ่ม
button_images = {
    "start": ("Str.png", "StrA.png"),
    "stop": ("Sto.png", "StoA.png"),
    "complete": ("Cop.png", "CopA.png"),
    "resets": ("Re.png", "ReA.png"),
}

images = {
    key: (
        ImageTk.PhotoImage(Image.open(os.path.join(assets_path, val[0])).resize((150, 50))),
        ImageTk.PhotoImage(Image.open(os.path.join(assets_path, val[1])).resize((150, 50)))
    )
    for key, val in button_images.items()
}

# ฟังก์ชันเปลี่ยนภาพเมื่อโฮเวอร์
def on_hover(button, img_hover):
    button.config(image=img_hover)

def on_leave(button, img_default):
    button.config(image=img_default)

# ฟังก์ชันจำลองปุ่มทำงาน
def start_action():
    status_var.set("Processing")
    start_camera()

def stop_action():
    status_var.set("Stopped")
    stop_camera()

def complete_action():
    status_var.set("Completed")

def reset_action():
    status_var.set("Resetting")

# เฟรมเก็บปุ่ม (ชิดซ้ายใต้ Status)
button_frame = tk.Frame(main_frame, bg="white")
button_frame.pack(pady=50, anchor="w")

# ปุ่ม Start และ Stop (แถวแรก)
start_button = tk.Button(button_frame, image=images["start"][0], borderwidth=0, command=start_action)
start_button.grid(row=0, column=0, padx=5, pady=5)
start_button.bind("<Enter>", lambda e: on_hover(start_button, images["start"][1]))
start_button.bind("<Leave>", lambda e: on_leave(start_button, images["start"][0]))

stop_button = tk.Button(button_frame, image=images["stop"][0], borderwidth=0, command=stop_action)
stop_button.grid(row=0, column=1, padx=5, pady=5)
stop_button.bind("<Enter>", lambda e: on_hover(stop_button, images["stop"][1]))
stop_button.bind("<Leave>", lambda e: on_leave(stop_button, images["stop"][0]))

# ปุ่ม Complete และ Resets (แถวที่สอง)
complete_button = tk.Button(button_frame, image=images["complete"][0], borderwidth=0, command=complete_action)
complete_button.grid(row=1, column=0, padx=5, pady=5)
complete_button.bind("<Enter>", lambda e: on_hover(complete_button, images["complete"][1]))
complete_button.bind("<Leave>", lambda e: on_leave(complete_button, images["complete"][0]))

resets_button = tk.Button(button_frame, image=images["resets"][0], borderwidth=0, command=reset_action)
resets_button.grid(row=1, column=1, padx=5, pady=5)
resets_button.bind("<Enter>", lambda e: on_hover(resets_button, images["resets"][1]))
resets_button.bind("<Leave>", lambda e: on_leave(resets_button, images["resets"][0]))

# ---------------------------- OpenCV Camera Frame (ฝั่งขวา) ----------------------------
camera_frame = tk.Frame(root, bg="white", bd=2, relief="solid")
camera_frame.pack(side=tk.RIGHT, padx=20, pady=20, anchor="ne")

# ✅ Label "OpenCV" อยู่นอกกรอบ และเพิ่มสี RGB เรียงกันในแกน X
# ✅ เพิ่ม Label ว่าง ๆ เพื่อเว้นบรรทัดก่อนกล้อง
tk.Label(root, text="", bg="white").pack(side=tk.TOP, anchor="ne", pady=5)  # เพิ่มระยะห่าง

# ✅ กรอบของ OpenCV Header (ขยับลงให้มีช่องว่าง)
header_frame = tk.Frame(root, bg="white")
header_frame.pack(side=tk.TOP, anchor="w", padx=20, pady=5)  # ชิดซ้าย

opencv_label = tk.Label(header_frame, text="OpenCV", font=("Arial", 18, "bold"), bg="white")
opencv_label.pack(side=tk.LEFT)

# ✅ สี RGB (แดง เขียว น้ำเงิน) จัดเรียงในแนว X
tk.Label(header_frame, text="  ", bg="red", width=2, height=1).pack(side=tk.LEFT, padx=2)
tk.Label(header_frame, text="  ", bg="green", width=2, height=1).pack(side=tk.LEFT, padx=2)
tk.Label(header_frame, text="  ", bg="blue", width=2, height=1).pack(side=tk.LEFT, padx=2)

# ✅ เพิ่ม Padding ด้านล่างของ header_frame ก่อนเริ่มกล้อง
header_frame.pack_configure(pady=15)

# ✅ ย้ายโลโก้ BOSCH และ UI ลงมาข้างล่างให้ OpenCV อยู่บนสุด
main_frame.pack(side=tk.LEFT, padx=20, pady=20, anchor="nw")

# ✅ กรอบแสดงกล้อง OpenCV
camera_frame = tk.Frame(root, bg="white", bd=2, relief="solid")
camera_frame.pack(side=tk.RIGHT, padx=20, pady=20, anchor="ne")

# ตั้งค่าขนาดของกล้องเป็นขนาดตายตัว
CAMERA_WIDTH = 900
CAMERA_HEIGHT = 640

canvas = tk.Canvas(camera_frame, width=CAMERA_WIDTH, height=CAMERA_HEIGHT, bg="gray", highlightthickness=0)
canvas.pack()

cap = None

def start_camera():
    global cap
    cap = cv2.VideoCapture(0)
    update_frame()

def stop_camera():
    global cap
    if cap and cap.isOpened():
        cap.release()
    canvas.delete("all")  # เคลียร์ภาพกล้อง

def update_frame():
    global cap
    if cap and cap.isOpened():
        ret, frame = cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (CAMERA_WIDTH, CAMERA_HEIGHT))
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            canvas.create_image(CAMERA_WIDTH // 2, CAMERA_HEIGHT // 2, anchor="center", image=imgtk)
            canvas.imgtk = imgtk
        canvas.after(10, update_frame)

# รันหน้าต่างหลัก
root.mainloop()
