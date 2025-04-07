from ultralytics import YOLO

model = YOLO("D:/yolov8/runs/detect/train4/weights/best.pt")

results = model("D:/yolov8/test/P38 (5).jpg")
results[0].show()