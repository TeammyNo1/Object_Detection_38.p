import cv2
from ultralytics import YOLO

# โหลดโมเดล YOLOv8
model = YOLO("D:/yolov8/yolov8n.pt")

# เปิดกล้อง (ใช้ 0 สำหรับกล้องหลัก หรือเปลี่ยนเป็นพาธไฟล์วิดีโอ)
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break  # ถ้าไม่สามารถอ่านเฟรมได้ ให้หยุดทำงาน

    # ใช้โมเดล YOLO ทำการตรวจจับวัตถุ
    results = model(frame)

    # วาดกรอบและแสดงผล
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])  # ดึงตำแหน่งของ bounding box
            conf = box.conf[0].item()  # ความแม่นยำของการตรวจจับ
            cls = int(box.cls[0])  # ประเภทของวัตถุที่ตรวจพบ
            label = f"{model.names[cls]}: {conf:.2f}"

            # วาดกรอบสี่เหลี่ยม
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # แสดงผลภาพ
    cv2.imshow("YOLOv8 Detection", frame)

    # กด 'q' เพื่อออกจากการทำงาน
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ปิดการทำงานของกล้องและหน้าต่าง OpenCV
cap.release()
cv2.destroyAllWindows()
