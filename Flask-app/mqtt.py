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

    def __init__(self):
        # MQTT Configuration
        self.MQTT_CLIENT_ID = "sic6_prototype"
        self.MQTT_BROKER = "broker.emqx.io"
        self.MQTT_TOPIC_SUB = "/UNI544/ADHYAKSAWARUNAPUTRO/data_sensor"
        self.MQTT_TOPIC_PUB = "/UNI544/ADHYAKSAWARUNAPUTRO/servo_angles"

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

    def __on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
            client.subscribe(self.MQTT_TOPIC_SUB)
        else:
            print(f"Failed to connect, return code {rc}")

    def __on_message(self, client, userdata, msg):
        data = msg.payload.decode()

        data = re.sub(r'NaN', '0', data, flags=re.IGNORECASE)
        print(f"Received data: {data}")
        try:
            self.current_data = json.loads(data)

            # Send data to Ubidots asynchronously
            self.__send_to_ubidots(self.current_data)

            # Insert data into MongoDB
            self.collection.insert_one(self.current_data)
            print("Data inserted into MongoDB.")

            # Publish to another topic if needed
            if self.current_data.get("status") == 1:
                print("From MQTT client: Fire Detected!")
                self.__publish()

        except json.JSONDecodeError:
            print("Received invalid JSON data!")

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

