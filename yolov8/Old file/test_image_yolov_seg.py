from ultralytics import YOLO

model = YOLO("D:/yolov8/yolov8n-seg.pt")

results = model("D:/yolov8/test/test1.jpg")
results[0].show()