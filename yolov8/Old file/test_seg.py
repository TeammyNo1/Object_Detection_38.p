import cv2
from ultralytics import YOLO

# โหลดโมเดล Segmentation
model = YOLO("D:\yolov8\yolov8n-seg.pt")

# เปิดกล้อง
cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    # ทำ segmentation
    results = model(frame)

    # แสดงผลลัพธ์
    for r in results:
        frame = r.plot()  # ใช้ plot() เพื่อแสดง bounding box และ mask บนภาพ

    cv2.imshow("YOLOv8 Segmentation", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
