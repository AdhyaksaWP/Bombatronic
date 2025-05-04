import os
import re
import requests
import json
from pymongo import MongoClient
# import asyncio
import paho.mqtt.client as mqtt

from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path('.env'))

class MQTT():

    def __init__(self, fire_detector):
        # MQTT Configuration
        self.MQTT_CLIENT_ID = "sic6_prototype"
        self.MQTT_BROKER = "broker.emqx.io"
        self.MQTT_TOPIC_SUB = "/UNI544/ADHYAKSAWARUNAPUTRO/data_sensor"
        self.MQTT_TOPIC_PUB = "/UNI544/ADHYAKSAWARUNAPUTRO/servo_angles"
        self.MQTT_TOPIC_SUB_CAM = "/UNI544/ADHYAKSAWARUNAPUTRO/cam_url"

        self.fire_detector = fire_detector
        self.__cur_url = None
        self.__prev_url = None

        self.client = mqtt.Client(client_id=self.MQTT_CLIENT_ID)
        self.client.on_connect = self.__on_connect
        self.client.on_message = self.__on_message

        self.current_data = None

        # Ubidots Configuration
        self.UBIDOTS_TOKEN = os.getenv("UBIDOTS_API_KEY")
        self.DEVICE_LABEL = "symbiot"

        self.UBIDOTS_URL = f"https://industrial.api.ubidots.com/api/v1.6/devices/{self.DEVICE_LABEL}/"
        self.HEADERS = {
            "X-Auth-Token": self.UBIDOTS_TOKEN,
            "Content-Type": "application/json"
        }
        self.MONGO_URI = os.getenv("MONGODB_URL")
        self.mongo_client = MongoClient(self.MONGO_URI)
        self.db = self.mongo_client["sensor"]
        self.collection = self.db["data_sensor"]
    
    def __convert_to_ppm(self):
        try:
            adc_mq7 = self.current_data["MQ7"]
            adc_mq135 = self.current_data["MQ135"]

            # ADS1115: 16-bit ADC, full-scale range ±6.144V → 32767 max
            volt_mq7 = max((adc_mq7 / 32767.0) * 6.144, 0.01)
            volt_mq135 = max((adc_mq135 / 32767.0) * 6.144, 0.01)

            # Hitung RS masing-masing sensor (Vcc = 5V, RL = 10kΩ)
            rs_mq7 = ((5.0 - volt_mq7) * 10000) / volt_mq7
            rs_mq135 = ((5.0 - volt_mq135) * 10000) / volt_mq135

            # --- MQ7: CO Sensor ---
            # Kalibrasi R₀: asumsi udara bersih = 1 ppm CO (nilai default 30)
            if not hasattr(self, 'r0_mq7'):
                assumed_ppm_co = 1.0
                a_mq7 = 99.042
                b_mq7 = -1.518
                self.r0_mq7 = rs_mq7 / ((assumed_ppm_co / a_mq7) ** (1 / b_mq7))
                print(f"[CALIB] MQ7 R0 set to: {self.r0_mq7:.2f} Ω")
            else:
                a_mq7 = 99.042
                b_mq7 = -1.518

            ratio_mq7 = rs_mq7 / self.r0_mq7
            ppm_mq7 = a_mq7 * (ratio_mq7 ** b_mq7)

            # --- MQ135: CO₂ Sensor ---
            # Kalibrasi R₀: asumsi udara indoor = 400 ppm CO2
            if not hasattr(self, 'r0_mq135'):
                assumed_ppm_co2 = 400.0
                a_mq135 = 110.47
                b_mq135 = -2.862
                self.r0_mq135 = rs_mq135 / ((assumed_ppm_co2 / a_mq135) ** (1 / b_mq135))
                print(f"[CALIB] MQ135 R0 set to: {self.r0_mq135:.2f} Ω")
            else:
                a_mq135 = 110.47
                b_mq135 = -2.862

            ratio_mq135 = rs_mq135 / self.r0_mq135
            ppm_mq135 = a_mq135 * (ratio_mq135 ** b_mq135)

            # Simpan hasil konversi ke dalam data
            self.current_data["MQ7"] = round(ppm_mq7, 2)
            self.current_data["MQ135"] = round(ppm_mq135, 2)

            # Log
            print(f"DHT11 - Temp : {self.current_data['Temp']}, Hum : {self.current_data['Hum']}")
            print(f"ADC MQ7: {adc_mq7} → V: {volt_mq7:.3f} V → RS: {rs_mq7:.2f} → RS/R0: {ratio_mq7:.2f} → CO: {ppm_mq7:.2f} ppm")
            print(f"ADC MQ135: {adc_mq135} → V: {volt_mq135:.3f} V → RS: {rs_mq135:.2f} → RS/R0: {ratio_mq135:.2f} → CO₂: {ppm_mq135:.2f} ppm")

        except (KeyError, ZeroDivisionError, TypeError) as e:
            print(f"[PPM Conversion Error]: {e}")


        
    def __on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
            client.subscribe(self.MQTT_TOPIC_SUB)
            client.subscribe(self.MQTT_TOPIC_SUB_CAM)
        else:
            print(f"Failed to connect, return code {rc}")

    def __on_message(self, client, userdata, msg):
        if msg.topic == self.MQTT_TOPIC_SUB:
            data = msg.payload.decode()

            data = re.sub(r'NaN', '0', data, flags=re.IGNORECASE)
            # print(f"Received data: {data}")
            try:
                self.current_data = json.loads(data)

                # Run the convert to ppm method
                self.__convert_to_ppm()

                # print("MQ7 after coversion: ", self.current_data["MQ7"])
                # print("MQ135 after coversion: ", self.current_data["MQ135"])

                # Send data to Ubidots asynchronously
                self.__send_to_ubidots(self.current_data)
                # print("Succesfully inserted")

                # Insert data into MongoDB
                self.collection.insert_one(self.current_data)
                # print("Data inserted into MongoDB.")

                # Publish to another topic if needed
                if self.current_data.get("status") == 1:
                    print("From MQTT client: Fire Detected!")
                    self.__publish()

            except json.JSONDecodeError:
                print("Received invalid JSON data!")
        
        elif msg.topic == self.MQTT_TOPIC_SUB_CAM:
            self.__cur_url = msg.payload.decode()
            if self.__cur_url != self.__prev_url:
                print(f"New camera URL received: {self.__cur_url}")
                self.__prev_url = self.__cur_url
                self.fire_detector.set_url(self.__cur_url)


    def __send_to_ubidots(self, data):
        try:
            response = requests.post(self.UBIDOTS_URL, json=data, headers=self.HEADERS)
            # print("Response from Ubidots:", response.text)

        except requests.RequestException as e:
            print("Error sending data to Ubidots:", e)

    def __publish(self):
        try:
            response = requests.get("http://127.0.0.1:5000/api/vision")
            print(f"Response from camera thread: {response.text}")
            self.client.publish(self.MQTT_TOPIC_PUB, response.text)

        except requests.RequestException as e:
            print("Error in publishing message:", e)

    def start(self):
        print("IN MQTT THREAD!")
        self.client.connect(self.MQTT_BROKER, 1883, 60)
        # self.client.loop_start()
        self.client.loop_forever()

