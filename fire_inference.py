import cv2
from ultralytics import YOLO

webcam = cv2.VideoCapture(0)

width, height = 640, 480

model = YOLO('./runs/detect/train14/weights/best.pt')

while True:
    ret, frame = webcam.read()
    if not ret:
        break
    
    frame = cv2.resize(frame, (width, height))
    results = model(frame, stream=True)

    for result in results:
        boxes = result.boxes

        for box in boxes:
            if box.conf > 0.55:
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                x_center, y_center, w, h = box.xywh[0]
                x_center, y_center, w, h = int(x_center), int(y_center), int(w), int(h)

                # Shift so that the center point is in the middle of the frame
                x_shifted = x_center - width // 2
                y_shifted = height // 2 - y_center

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)

                shifted_x = width // 2 + x_shifted
                shifted_y = height // 2 - y_shifted
                cv2.circle(frame, (shifted_x, shifted_y), 3, (0, 0, 255), -1)

                cv2.putText(frame, f"Confidence: {(box.conf[0] * 100):.2%f}", (x1, y1 - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    cv2.imshow("Camera Frame", frame)
    
    if cv2.waitKey(1) == ord('q'):
        break

webcam.release()
cv2.destroyAllWindows()
