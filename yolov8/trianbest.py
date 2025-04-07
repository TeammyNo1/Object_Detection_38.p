from ultralytics import YOLO

model = YOLO(r"D:\yolov8\runs\detect\train6\weights\best.pt")

train_results = model.train(
    data=r"D:\yolov8\datasets\data.yaml",
    epochs=500,        # ✅ Train ได้นานขึ้น
    imgsz=640,
    batch=16,          # ✅ ลด Batch ให้ใช้ VRAM น้อยลง
    device="0",
    workers=0,
    pretrained=True,   # ✅ ใช้ Weights จาก `best.pt`
    amp=True,          # ✅ ลด VRAM ด้วย Automatic Mixed Precision
    half=True,         # ✅ ใช้ FP16 ลด VRAM
    cache=False,       # ✅ ปิด Cache เพื่อลดการใช้ RAM/VRAM
    patience=50,       # ✅ Early Stopping ถ้า Accuracy ไม่เพิ่มขึ้น
    lr0=0.001,         # ✅ ลด Learning Rate ป้องกัน Overfitting
    translate=0.1,     # ✅ Data Augmentation
    scale=0.5,
    fliplr=0.5
)

# ประเมินผลหลังการเทรน
metrics = model.val()
