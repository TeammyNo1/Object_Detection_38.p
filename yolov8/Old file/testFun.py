import tkinter as tk
from PIL import Image, ImageTk
import cv2
from ultralytics import YOLO
from datetime import datetime

# โหลดโมเดล YOLO
model_path = r"D:\yolov8\runs\detect\train4\weights\best.pt"
model = YOLO(model_path)

# ตัวแปร
p38_per_layer = 34  # จำกัดสูงสุดที่ 34 ชิ้นต่อชั้น
total_layers = 5  # 5 ชั้นต่อกล่อง
total_p38_per_box = p38_per_layer * total_layers  # 170 ชิ้นต่อกล่อง
current_layer = 1  # เริ่มต้นชั้นที่ 1
total_p38 = 0  # จำนวน P38 ที่นับได้ในกล่องปัจจุบัน
pc_total = 1  # จำนวนแผ่นกระดาษ (เริ่มที่ 1 เพราะวางแผ่นแรกในกล่อง)
box_count = 0  # จำนวนกล่องที่เสร็จสมบูรณ์

# ฟังก์ชันเริ่มต้นกล้อง
def start_camera():
    global cap
    cap = cv2.VideoCapture(0)
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
            results = model(frame, conf=0.5)
            current_count = 0
            for result in results:
                for box in result.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    conf = box.conf[0].item()
                    cls = int(box.cls[0].item())
                    if cls == 0:
                        current_count += 1
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(frame, f"P38 ({conf:.2f})", (x1, y1 - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # จำกัดค่า P38 ไม่ให้เกิน 34
            current_count = min(current_count, p38_per_layer)

            p38_var.set(str(current_count))
            p38_total_var.set(f"{total_p38 + current_count}/{total_p38_per_box}")

            if current_count >= p38_per_layer:
                status_var.set("Fully")
                complete_button.config(state=tk.NORMAL, image=images["complete"][1])  # ปุ่มสีฟ้า
                resets_button.config(state=tk.NORMAL, image=images["resets"][1])  # เปิดปุ่ม Resets
                stop_camera()
            else:
                status_var.set("Processing")
                complete_button.config(state=tk.DISABLED, image=images["complete"][0])  # ปุ่มยังเป็นสีเทา
                resets_button.config(state=tk.DISABLED, image=images["resets"][0])  # ปิดปุ่ม Resets

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            camera_label.imgtk = imgtk
            camera_label.configure(image=imgtk)
        camera_label.after(10, update_frame)

# ฟังก์ชัน Complete (เมื่อกด Complete จะบันทึกและไปชั้นถัดไป)
def complete_action():
    global current_layer, total_p38, pc_total, box_count
    current_count = int(p38_var.get())  # อ่านค่าจาก UI

    if current_count < p38_per_layer:
        return  # ออกหาก P38 ยังไม่ครบ

    if current_layer < total_layers:
        current_layer += 1
        pc_total += 1
        total_p38 += p38_per_layer
        pc_total_var.set(f"{pc_total}/{total_layers+1}")  # +1 เพราะมีแผ่นรองเริ่มต้น
        status_var.set("Processing")
        start_camera()
    else:
        total_p38 += p38_per_layer
        box_count += 1
        current_layer = 1
        pc_total = 1
        total_p38 = 0
        box_count_var.set(str(box_count))
        status_var.set("Ready")

    # ปิดปุ่ม Complete หลังจากกด
    complete_button.config(state=tk.DISABLED, image=images["complete"][0])

# ฟังก์ชัน Resets (รีเซ็ตค่า P38 และเริ่มกล้องใหม่)
def reset_p38():
    if int(p38_var.get()) >= p38_per_layer:  # รีเซ็ตได้เมื่อ P38 ครบ 34 เท่านั้น
        p38_var.set("0")  # รีเซ็ตค่า P38 เท่านั้น
        status_var.set("Processing")  # ตั้งค่าให้เป็น Processing
        resets_button.config(state=tk.DISABLED, image=images["resets"][0])  # ปิดปุ่ม Resets หลังจากกด
        start_camera()  # เริ่มกล้องใหม่เพื่อจับชิ้นงานอีกครั้ง

# ฟังก์ชันแสดงวันที่
def update_date():
    today = datetime.now().strftime("%d/%m/%Y")
    date_var.set(f"Date: {today}")

# ฟังก์ชันเปลี่ยนภาพเมื่อโฮเวอร์
def on_hover(button, img_hover):
    button.config(image=img_hover)

def on_leave(button, img_default):
    button.config(image=img_default)

# เริ่มต้น UI
root = tk.Tk()
root.title("Project P38 ")
root.geometry("1100x650")
root.configure(bg="white")

# Header
header_frame = tk.Frame(root, bg="white")
header_frame.pack(fill=tk.X, pady=10)

date_var = tk.StringVar()
tk.Label(header_frame, textvariable=date_var, font=("Arial", 14), fg="black", bg="white").pack(side=tk.RIGHT, padx=10)

# กล้อง
camera_frame = tk.Frame(root, bg="white", relief="solid", bd=2)
camera_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=10)
camera_label = tk.Label(camera_frame, bg="gray")
camera_label.pack(fill=tk.BOTH, expand=True)

# ตัวแปร UI
status_var = tk.StringVar(value="Ready")
p38_var = tk.StringVar(value="0")  # ✅ เพิ่มตัวแปรที่หายไป
p38_total_var = tk.StringVar(value="0/170")  # ✅ เพิ่มตัวแปรที่หายไป
pc_total_var = tk.StringVar(value="1/6")
box_count_var = tk.StringVar(value="0")

# โหลดรูปภาพปุ่ม
buttons = {
    "start": ("Str.png", "StrA.png"),
    "stop": ("Sto.png", "StoA.png"),
    
    "complete": ("Cop.png", "CopA.png"),
    "resets": ("Re.png", "ReA.png"),
}

images = {key: (ImageTk.PhotoImage(Image.open(f"D:/yolov8/assets/{val[0]}").resize((150, 50))),
                ImageTk.PhotoImage(Image.open(f"D:/yolov8/assets/{val[1]}").resize((150, 50)))) for key, val in buttons.items()}

# ปุ่ม
button_frame = tk.Frame(root, bg="white")
button_frame.pack(pady=20)

# ปุ่ม Start
start_button = tk.Button(button_frame, image=images["start"][0], borderwidth=0, command=start_camera)
start_button.pack(side=tk.LEFT, padx=5)
start_button.bind("<Enter>", lambda e: on_hover(start_button, images["start"][1]))
start_button.bind("<Leave>", lambda e: on_leave(start_button, images["start"][0]))

# ปุ่ม Stop
stop_button = tk.Button(button_frame, image=images["stop"][0], borderwidth=0, command=stop_camera)
stop_button.pack(side=tk.LEFT, padx=5)
stop_button.bind("<Enter>", lambda e: on_hover(stop_button, images["stop"][1]))
stop_button.bind("<Leave>", lambda e: on_leave(stop_button, images["stop"][0]))

# ปุ่ม Complete
complete_button = tk.Button(button_frame, image=images["complete"][0], borderwidth=0, command=complete_action, state=tk.DISABLED)
complete_button.pack(side=tk.LEFT, padx=5)

# ปุ่ม Resets
resets_button = tk.Button(button_frame, image=images["resets"][0], borderwidth=0, command=reset_p38, state=tk.DISABLED)
resets_button.pack(side=tk.LEFT, padx=5)

update_date()
root.mainloop()
