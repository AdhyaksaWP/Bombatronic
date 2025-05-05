import json
import time
import cv2
import urllib.request
import numpy as np
from ultralytics import YOLO

class Fire_Inference():
    def __init__(self):
        self.__url = 'http://192.168.187.120/cam-lo.jpg'
        self.__width = 320
        self.__height = 240
        # self.__serial = serial.Serial('/dev/ttyUSB0', baudrate=115200)
        self.__model = YOLO('./output/yolo_model.pt')
        self.__yaw_start_angle = 90 
        self.__pitch_start_angle = 150
        self.__cur_yaw = self.__yaw_start_angle
        self.__cur_pitch = self.__pitch_start_angle
        
        self.frame = None
        self.running = True


    def set_url(self, url_json):
        # Parse JSON string if it's not already a dict
        if isinstance(url_json, str):
            url_data = json.loads(url_json)
        else:
            url_data = url_json

        # Extract and clean the URL
        raw_ip = url_data["url"].strip()  # removes \r, \n, spaces
        cam_url = f"http://{raw_ip}/cam-lo.jpg"
        
        print(f"[Fire_Inference] Camera URL updated to: {cam_url}")
        self.__url = cam_url


    def camera(self):
        while self.running:
            # try:
            if not self.__url:
                time.sleep(0.1)
                continue

            img_resp = urllib.request.urlopen(self.__url)
            imgnp = np.array(bytearray(img_resp.read()), dtype=np.uint8)
            self.frame = cv2.imdecode(imgnp, -1)

            cv2.line(self.frame, (self.__width//2, 0), (self.__width//2, self.__height), (0, 0, 255), 5)
            cv2.line(self.frame, (0, self.__height//2), (self.__width, self.__height//2), (0, 0, 255), 5)

            cv2.imshow("Camera Frame", self.frame)

            if cv2.waitKey(1) == ord('q'):
                break
            # except Exception as e:
            #     # print(f"Camera error: {e}")

        cv2.destroyAllWindows()
    
    def inference(self):
        if self.frame is None:
            print("No frame available for inference")
            return 90, 135

        results = self.__model(self.frame, stream=True, verbose=False)
        for result in results:
            boxes = result.boxes

            for box in boxes:
                confidence = box.conf[0].item()
                if confidence > 0.01:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    x_center, y_center, w, h = map(int, box.xywh[0])

                    # Shift the center to make (0,0) the middle of the frame
                    x_shifted = x_center - (self.__width // 2)
                    y_shifted = y_center - (self.__height // 2)  

                    THRESHOLD_X = 50  # Pixels
                    THRESHOLD_Y = 50  # Pixels

                    # Adjust angles only if deviation exceeds the threshold
                    if abs(x_shifted) > THRESHOLD_X or abs(y_shifted) > THRESHOLD_Y:
                        yaw, pitch = self.__frame_to_servo_angles(x_shifted, y_shifted, self.__width, self.__height)
                        print(f"Target Angles - YAW: {yaw}°, PITCH: {pitch}°")

                        self.__cur_yaw = yaw
                        self.__cur_pitch = pitch

                        # self.__serial.write(f"{yaw:.1f},{pitch:.1f}\n".encode())
                    else:
                        print("Object is already centered, no adjustment needed")

                    return self.__cur_yaw, self.__cur_pitch
                
        print("No fire detected, returning last known angles")
        return self.__cur_yaw, self.__cur_pitch
        
    def __frame_to_servo_angles(self, x_pixel, y_pixel, frame_width, frame_height, fov_x=60, fov_y=45):
        degrees_per_pixel_x = fov_x / frame_width
        degrees_per_pixel_y = fov_y / frame_height

        yaw_offset = x_pixel * degrees_per_pixel_x
        pitch_offset = y_pixel * degrees_per_pixel_y

        yaw_angle = self.__yaw_start_angle + yaw_offset
        pitch_angle = self.__pitch_start_angle + pitch_offset

        yaw_angle = max(0, min(180, yaw_angle))
        pitch_angle = max(0, min(180, pitch_angle))

        return int(yaw_angle), int(pitch_angle)
    
