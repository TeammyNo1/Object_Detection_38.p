from ultralytics import YOLO

# โหลดโมเดล yolov8n.pt
model = YOLO(r"D:\yolov8\yolov8n.pt")

# เทรนโมเดล (รอบแรก)
train_results = model.train(
    data=r"D:\yolov8\datasets\data.yaml",
    epochs=100,       # ✅ เทรน 100 รอบ
    imgsz=640,        # ✅ ขนาดภาพ 640x640
    batch=16,         # ✅ ใช้ Batch Size 32
    device="0",       # ✅ ใช้ GPU
    workers=0,        # ✅ ลดการใช้ CPU Workers
    pretrained=False, # 🔥 ปิด Pretrained ป้องกันโหลดไฟล์ใหม่
    amp=False,        # 🔥 ปิด Automatic Mixed Precision เพื่อไม่ให้โหลดไฟล์เพิ่ม
    optimizer="SGD",  # ✅ ใช้ Optimizer กำหนดเอง ไม่ใช้ค่า default ที่อาจโหลดไฟล์อื่น
    cache="disk"      # ✅ เปลี่ยน Cache เป็น Disk ป้องกันค่าที่เปลี่ยนแปลงเอง
)
# ประเมินผลหลังการเทรน
metrics = model.val()



