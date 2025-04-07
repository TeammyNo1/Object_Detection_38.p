import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import cv2
from ultralytics import YOLO
from datetime import datetime

# โหลดโมเดล YOLO ที่ฝึกแล้ว
model_path = r"D:\yolov8\runs\detect\train4\weights\best.pt"  # เปลี่ยนเป็น path ของโมเดล D:\Yolov11\runs\detect\train4\weights\best.pt
model = YOLO(model_path)

# ตัวแปร
p38_per_layer = 34  # จำนวน P38 ต่อชั้น
total_layers = 5    # จำนวนชั้นทั้งหมดต่อกล่อง
current_layer = 1   # ชั้นงานปัจจุบัน
total_p38 = 0       # จำนวน P38 ทั้งหมดในกล่อง
pc_total = 1        # จำนวนแผ่นกระดาษ (เริ่มจากแผ่นแรกในกล่อง)
box_count = 0       # จำนวนกล่องเริ่มต้นเป็น 0

# ฟังก์ชันเริ่มต้นกล้องและแสดงผลภาพ
def start_camera():
    global cap
    cap = cv2.VideoCapture(0)  # กล้องหลัก
    update_frame()

def stop_camera():
    global cap
    if cap.isOpened():
        cap.release()
    camera_label.config(image="")

def update_frame():
    global cap, current_layer, total_p38, pc_total, box_count
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            # ทำการตรวจจับวัตถุด้วย YOLO
            results = model(frame, conf=0.5)  # ความมั่นใจขั้นต่ำที่ 50%
            current_count = 0  # ตัวนับจำนวน P38 ในเฟรมปัจจุบัน

            for result in results:
                for box in result.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])  # พิกัดกรอบ
                    conf = box.conf[0].item()  # ค่าความมั่นใจ
                    cls = int(box.cls[0].item())  # Class ID
                    label = f"P38"
                    
                    # ถ้า class ID เป็น P38 (แก้ไขตามที่กำหนดใน dataset)
                    if cls == 0:  # Class ID 0 หมายถึง P38
                        current_count += 1
                        # วาดกรอบและแสดง label
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # จำกัดจำนวนชิ้นงานไม่ให้เกิน 34 ชิ้น
            if current_count > p38_per_layer:
                current_count = p38_per_layer

            # อัปเดตจำนวน P38 ใน UI (แบบเรียลไทม์)
            p38_var.set(str(current_count))
            p38_total_var.set(f"{total_p38 + current_count}/{p38_per_layer * total_layers}")

            # ตรวจสอบสถานะ
            if current_count >= p38_per_layer:
                status_var.set("Fully")
                complete_button.config(state=tk.NORMAL)  # เปิดใช้งานปุ่ม "Complete"
                messagebox.showinfo("Layer Complete", f"Layer {current_layer} is complete. Please press 'Complete' to continue.")
                stop_camera()
            else:
                status_var.set("Processing")
                complete_button.config(state=tk.DISABLED)  # ปิดใช้งานปุ่ม "Complete"

            # แปลงภาพจาก OpenCV (BGR) เป็น Tkinter-compatible (RGB)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            camera_label.imgtk = imgtk
            camera_label.configure(image=imgtk)
        camera_label.after(10, update_frame)

# ฟังก์ชันสำหรับปุ่ม "Complete"
def complete_action():
    global current_layer, total_p38, pc_total, box_count
    current_count = int(p38_var.get())  # จำนวน P38 ในเฟรมปัจจุบัน

    # ตรวจสอบว่าจำนวนชิ้นงานครบ 34 ชิ้นหรือไม่
    if current_count < p38_per_layer:
        messagebox.showwarning("Incomplete", f"Layer {current_layer} is not complete. Only {current_count} P38 detected.")
        return

    # อัปเดตสถานะและข้อมูล
    if current_layer < total_layers:
        current_layer += 1
        pc_total += 1
        total_p38 += p38_per_layer
        pc_total_var.set(f"{pc_total}/{total_layers + 1}")
        status_var.set("Processing")
        start_camera()
    else:
        total_p38 += p38_per_layer
        box_count += 1
        current_layer = 1
        pc_total = 1
        total_p38 = 0
        pc_total_var.set(f"{pc_total}/{total_layers + 1}")
        box_count_var.set(str(box_count))
        status_var.set("Ready")
        messagebox.showinfo("Box Complete", f"Box {box_count} is complete. Starting Box {box_count + 1}.")

    # ปิดใช้งานปุ่ม "Complete" หลังจากเสร็จสิ้น
    complete_button.config(state=tk.DISABLED)

# ฟังก์ชันสำหรับปุ่ม "Start"
def start_action():
    status_var.set("Processing")
    start_camera()

# ฟังก์ชันสำหรับปุ่ม "Stop"
def stop_action():
    status_var.set("Stopped")
    stop_camera()

# ฟังก์ชันสำหรับปุ่ม "Stop Program"
def reset_action():
    p38_var.set("0")  # รีเซ็ตเฉพาะค่า P38
    status_var.set("Processing")
    start_camera()

# ฟังก์ชันแสดงวันที่
def update_date():
    today = datetime.now().strftime("%d/%m/%Y")
    date_var.set(f"Date: {today}")

# สร้างหน้าต่างหลัก
root = tk.Tk()
root.title("Project P38 ")
root.geometry("1000x600")
root.configure(bg="#D9D9D9")  # เปลี่ยนพื้นหลัง

# ส่วนหัว
header_frame = tk.Frame(root, bg="#D9D9D9")  # เปลี่ยนพื้นหลัง
header_frame.pack(fill=tk.X, pady=10)

# เพิ่มข้อความ BOSCH
tk.Label(header_frame, text="BOSCH", font=("Arial", 24, "bold"), fg="red", bg="#D9D9D9").pack(side=tk.LEFT, padx=10)

date_var = tk.StringVar()
tk.Label(header_frame, textvariable=date_var, font=("Arial", 14), fg="black", bg="#D9D9D9").pack(side=tk.RIGHT, padx=10)
update_date()  # อัปเดตวันที่เริ่มต้น

# กล้องและการแสดงผล
camera_frame = tk.Frame(root, bg="#D9D9D9")  # เปลี่ยนพื้นหลัง
camera_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=10)

camera_label = tk.Label(camera_frame, bg="gray")
camera_label.pack(fill=tk.BOTH, expand=True)

# ข้อมูลและฟอร์ม
form_frame = tk.Frame(root, bg="#D9D9D9")  # เปลี่ยนพื้นหลัง
form_frame.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=10)

tk.Label(form_frame, text="P38", font=("Arial", 14), fg="black", bg="#D9D9D9").grid(row=0, column=0, sticky=tk.W)
p38_var = tk.StringVar(value="0")  # ตัวแปรแสดงจำนวน P38
tk.Entry(form_frame, font=("Arial", 14), textvariable=p38_var, state="readonly").grid(row=0, column=1, pady=5)

tk.Label(form_frame, text="P38 Total / Box", font=("Arial", 14), fg="black", bg="#D9D9D9").grid(row=1, column=0, sticky=tk.W)
p38_total_var = tk.StringVar(value="0/170")
tk.Entry(form_frame, font=("Arial", 14), textvariable=p38_total_var, state="readonly").grid(row=1, column=1, pady=5)

tk.Label(form_frame, text="Pc Total", font=("Arial", 14), fg="black", bg="#D9D9D9").grid(row=2, column=0, sticky=tk.W)
pc_total_var = tk.StringVar(value="1/6")
tk.Entry(form_frame, font=("Arial", 14), textvariable=pc_total_var, state="readonly").grid(row=2, column=1, pady=5)

tk.Label(form_frame, text="Box Count", font=("Arial", 14), fg="black", bg="#D9D9D9").grid(row=3, column=0, sticky=tk.W)
box_count_var = tk.StringVar(value="0")  # เริ่มต้น Box Count เป็น 0
tk.Entry(form_frame, font=("Arial", 14), textvariable=box_count_var, state="readonly").grid(row=3, column=1, pady=5)

tk.Label(form_frame, text="Status", font=("Arial", 14), fg="black", bg="#D9D9D9").grid(row=4, column=0, sticky=tk.W)
status_var = tk.StringVar(value="Ready")
tk.Label(form_frame, textvariable=status_var, font=("Arial", 14), fg="blue", bg="#D9D9D9").grid(row=4, column=1, sticky=tk.W)

# ปุ่ม
button_frame = tk.Frame(form_frame, bg="#D9D9D9")  # เปลี่ยนพื้นหลัง
button_frame.grid(row=5, column=0, columnspan=2, pady=20)

tk.Button(button_frame, text="Start", font=("Arial", 14), bg="green", fg="white", command=start_action).pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="Stop", font=("Arial", 14), bg="red", fg="white", command=stop_action).pack(side=tk.LEFT, padx=5)

complete_button = tk.Button(button_frame, text="Complete", font=("Arial", 14), bg="yellow", fg="black", command=complete_action, state=tk.DISABLED)
complete_button.pack(side=tk.LEFT, padx=5)

resets_button = tk.Button(button_frame, text="Resets", font=("Arial", 14), bg="gray", fg="white", command=reset_action)
resets_button.pack(side=tk.LEFT, padx=5)

# เริ่มต้น Tkinter
root.mainloop()
