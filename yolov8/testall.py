import tkinter as tk
from PIL import Image, ImageTk
import os
import cv2
from ultralytics import YOLO  
from tkinter import messagebox
from datetime import datetime

# โหลดโมเดล YOLO
model_path = r"D:\yolov8\runs\detect\train4\weights\best.pt"
model = YOLO(model_path)

# ตั้งค่า path ของรูปภาพปุ่มและโลโก้
assets_path = r"D:\yolov8\assets"
logo_path = os.path.join(assets_path, "BOSCH_LOGO.png")

# เริ่มต้นหน้าต่างหลัก
root = tk.Tk()
root.title("P38 AI Detection")
root.geometry("1280x740")
root.configure(bg="white")

# โหลดโลโก้และปรับขนาด
logo_img = Image.open(logo_path).resize((250, 80))
logo_photo = ImageTk.PhotoImage(logo_img)

# สร้าง Layout หลัก
main_frame = tk.Frame(root, bg="white")
main_frame.pack(side=tk.LEFT, padx=20, pady=20, anchor="nw")

# แสดงโลโก้
logo_label = tk.Label(main_frame, image=logo_photo, bg="white")
logo_label.pack(anchor="w", pady=5)

# ตัวแปรแสดงข้อมูล
p38_var = tk.StringVar(value="0")
p38_total_var = tk.StringVar(value="0/170")
pc_total_var = tk.StringVar(value="1/6")
box_count_var = tk.StringVar(value="0")
status_var = tk.StringVar(value="Ready")

# ค่าตั้งต้น
p38_per_layer = 34  
total_layers = 5  
total_p38_per_box = p38_per_layer * total_layers  
current_layer = 1  
total_p38 = 0  
pc_total = 1  
box_count = 0  
cap = None  # ตัวแปรเก็บกล้อง
is_camera_stopped = False  # ตัวแปรเช็คว่ากล้องหยุดหรือไม่

# ฟังก์ชันสร้างช่องป้อนค่าพร้อม Label
def create_entry(parent, label_text, text_var, row):
    tk.Label(parent, text=label_text, font=("Arial", 16, "bold"), bg="white").grid(
        row=row, column=0, sticky="w", padx=10, pady=2
    )
    entry = tk.Entry(
        parent, textvariable=text_var, 
        font=("Arial", 16),
        state="readonly", 
        width=25,  
        relief="solid"
    )
    entry.grid(row=row + 1, column=0, padx=10, pady=5, sticky="we")

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

# ✅ ฟังก์ชันอัปเดตสถานะและเปลี่ยนสี
def update_status(new_status):
    status_var.set(new_status)  # อัปเดตข้อความ

    # ✅ กำหนดสีตามเงื่อนไข
    color_mapping = {
        "Processing": "#FF7F50",   # Coral
        "Stopcamera": "#000080",   # Navy
        "Fully": "#56cd78",        
        "Complete": "#00FF00"      # Green
    }

    # เปลี่ยนสีข้อความใน Entry
    status_entry.config(fg=color_mapping.get(new_status, "blue"))  # ถ้าไม่มีใน mapping ใช้สีดำ

# ✅ ปรับให้ทุกที่ที่มี `status_var.set(...)` เปลี่ยนเป็น `update_status(...)`
# ฟังก์ชันเริ่มต้นกล้อง
def start_camera():
    global cap, is_camera_stopped
    if is_camera_stopped:
        is_camera_stopped = False
    cap = cv2.VideoCapture(0)
    update_status("Processing")  # ✅ อัปเดตสถานะ
    update_frame()

# ฟังก์ชันหยุดกล้อง
def stop_camera():
    global cap
    if cap.isOpened():
        cap.release()
    camera_label.config(image="")
    update_status("Stopcamera")  # ✅ อัปเดตสถานะ

# ฟังก์ชัน Reset
def reset_action():
    global total_p38, current_layer
    p38_var.set("0")  # รีเซ็ตค่า P38 ในชั้นนี้
    update_status("Processing")  # ✅ อัปเดตสถานะ
    complete_button.config(state=tk.DISABLED)  # ปิดปุ่ม Complete อีกครั้ง
    resets_button.config(state=tk.DISABLED)  # ปิดปุ่ม Reset อีกครั้ง
    start_camera()  # เริ่มกล้องใหม่


# ✅ ตัวแปร Date
date_var = tk.StringVar()

# ✅ ฟังก์ชันอัปเดตวันที่
def update_date():
    today = datetime.now().strftime("%d/%m/%Y")
    date_var.set(f"Date: {today}")


def update_frame():
    global cap, current_layer, total_p38, pc_total, box_count
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            results = model(frame, conf=0.6)  # ความมั่นใจขั้นต่ำที่ 60%
            current_count = 0  

            for result in results:
                for box in result.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])  
                    conf = box.conf[0].item()  
                    cls = int(box.cls[0].item())  
                    label = f"P38"

                    if cls == 0:  
                        current_count += 1
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            if current_count > p38_per_layer:
                current_count = p38_per_layer

            p38_var.set(str(current_count))
            p38_total_var.set(f"{total_p38 + current_count}/{p38_per_layer * total_layers}")

            if current_count >= p38_per_layer:
                update_status("Fully")  # ✅ อัปเดตสถานะ
                complete_button.config(state=tk.NORMAL)  
                resets_button.config(state=tk.NORMAL)  
                complete_button.config(image=images["complete"][1])
                resets_button.config(image=images["resets"][0])  
                if status_var.get() != "Completed":
                    messagebox.showinfo("Layer Complete", f"Layer {current_layer} is full.\nPlease click 'Complete'\n'Reset' to continue.")
                    stop_camera()
                    update_status("Completed")  
            else:
                update_status("Processing")  # ✅ อัปเดตสถานะ
                complete_button.config(state=tk.DISABLED)  
                resets_button.config(state=tk.DISABLED)  
                complete_button.config(image=images["complete"][0])  

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            camera_label.imgtk = imgtk
            camera_label.configure(image=imgtk)

        camera_label.after(10, update_frame)

# ✅ ฟังก์ชันสำหรับปุ่ม "Complete"
def complete_action():
    global current_layer, total_p38, pc_total, box_count
    current_count = int(p38_var.get())

    if current_count < p38_per_layer:
        messagebox.showwarning("Incomplete", f"Layer {current_layer} is not complete. Only {current_count} P38 detected.")
        return

    if current_layer < total_layers:
        current_layer += 1
        pc_total += 1
        total_p38 += p38_per_layer
        pc_total_var.set(f"{pc_total}/{total_layers + 1}")
        update_status("Processing")  # ✅ อัปเดตสถานะ
        start_camera()
    else:
        total_p38 += p38_per_layer
        box_count += 1
        current_layer = 1
        pc_total = 1
        total_p38 = 0
        pc_total_var.set(f"{pc_total}/{total_layers + 1}")
        box_count_var.set(str(box_count))
        update_status("Complete")  # ✅ อัปเดตสถานะ
        messagebox.showinfo("Box Complete", f"Box {box_count} is complete. Starting Box {box_count + 1}.")

    complete_button.config(state=tk.DISABLED)


# ✅ ฟังก์ชันเปลี่ยนภาพเมื่อเมาส์โฮเวอร์
def on_hover(button, new_image):
    button.config(image=new_image)
    button.image = new_image  # ป้องกันภาพหายไป

# ✅ ฟังก์ชันคืนภาพปุ่มเมื่อเมาส์ออก
def on_leave(button, original_image):
    button.config(image=original_image)
    button.image = original_image  # ป้องกันภาพหายไป

# โหลดรูปภาพปุ่ม
button_images = {
    "start": ("Str.png", "StrA.png"),
    "stop": ("Sto.png", "StoA.png"),
    "complete": ("Cop.png", "CopA.png"),
    "resets": ("Re.png", "ReA.png"),
}

images = {key: (ImageTk.PhotoImage(Image.open(f"D:/yolov8/assets/{val[0]}").resize((150, 50))),
                ImageTk.PhotoImage(Image.open(f"D:/yolov8/assets/{val[1]}").resize((150, 50)))) for key, val in button_images.items()}

# ✅ สร้างปุ่มในตาราง 2×2
button_frame = tk.Frame(main_frame, bg="white")
button_frame.pack(pady=20, anchor="w")


header_frame = tk.Frame(root, bg="white")
header_frame.pack(side=tk.TOP, anchor="w", padx=20)  # ❌ ไม่เพิ่ม pady ตรงนี้

# ✅ สร้าง Label แสดงวันที่ที่มุมขวาบน
date_label = tk.Label(root, textvariable=date_var, font=("Arial", 14, "bold"), bg="white")
date_label.place(relx=1.0, y=45, anchor="ne", x=-20)  # ขยับไปมุมขวาบน

# ✅ ขยับ OpenCV ลงมาโดยใช้ pady
opencv_label = tk.Label(header_frame, text="OpenCV", font=("Arial", 18, "bold"), bg="white")
opencv_label.pack(side=tk.LEFT, pady=45)  # 🔹 เพิ่มแค่ตรงนี้เพื่อขยับลงมา

# ✅ ขยับสี RGB ลงมาตาม OpenCV
tk.Label(header_frame, text="  ", bg="red", width=2, height=1).pack(side=tk.LEFT, padx=2, pady=10)
tk.Label(header_frame, text="  ", bg="green", width=2, height=1).pack(side=tk.LEFT, padx=2, pady=10)
tk.Label(header_frame, text="  ", bg="blue", width=2, height=1).pack(side=tk.LEFT, padx=2, pady=10)


# ✅ ปุ่ม Start (row 0, column 0)
start_button = tk.Button(button_frame, image=images["start"][0], borderwidth=0, command=start_camera)
start_button.grid(row=0, column=0, padx=5, pady=5)
start_button.bind("<Enter>", lambda e: on_hover(start_button, images["start"][1]))
start_button.bind("<Leave>", lambda e: on_leave(start_button, images["start"][0]))

# ✅ ปุ่ม Stop (row 0, column 1)
stop_button = tk.Button(button_frame, image=images["stop"][0], borderwidth=0, command=stop_camera)
stop_button.grid(row=0, column=1, padx=5, pady=5)
stop_button.bind("<Enter>", lambda e: on_hover(stop_button, images["stop"][1]))
stop_button.bind("<Leave>", lambda e: on_leave(stop_button, images["stop"][0]))

# ✅ ปุ่ม Complete (row 1, column 0)
complete_button = tk.Button(button_frame, image=images["complete"][0], borderwidth=0, command=complete_action, state=tk.DISABLED)
complete_button.grid(row=1, column=0, padx=5, pady=5)

# ✅ ปุ่ม Resets (row 1, column 1)
resets_button = tk.Button(button_frame, image=images["resets"][1], borderwidth=0, command=reset_action, state=tk.DISABLED)
resets_button.grid(row=1, column=1, padx=5, pady=5)


# เพิ่มกล้อง OpenCV ใน GUI
# สร้างเฟรมของกล้อง OpenCV
camera_frame = tk.Frame(root, bg="white", bd=2, relief="solid")
camera_frame.pack(side=tk.RIGHT, padx=20, pady=20, anchor="ne")

# สร้างป้ายแสดงภาพจากกล้อง
camera_label = tk.Label(camera_frame, bg="gray", width=940, height=640)
camera_label.pack(fill=tk.BOTH, expand=True)

update_date()
root.mainloop()