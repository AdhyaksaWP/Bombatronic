import os
import pandas as pd

from pymongo import MongoClient
from datetime import datetime

from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path('.env'))

class DB():

    def __init__(self):
        self.MONGO_URI = os.getenv("MONGODB_URL")
        self.mongo_client = MongoClient(self.MONGO_URI)
        self.db = self.mongo_client["sensor"]
        self.collection = self.db["data_sensor"]

    def fetch_db(self):
        cursor = self.collection.find().sort("_id", -1).limit(5)
        df = pd.DataFrame(cursor)
        if "timestamp" not in df.columns:
            if "_id" in df.columns:
                df["timestamp"] = df["_id"].apply(lambda x: x.generation_time)
            else:
                df["timestamp"] = datetime.utcnow()

        # Ubah ke datetime dan urutkan
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp")

        if df.empty:
            return {
                "Error": "Data is still empty!"
            }
        else:
            x = df['timestamp'].dt.strftime("%H:%M:%S") if 'timestamp' in df.columns else list(range(len(df)))
            y1 = df["MQ7"].fillna(0) if "MQ7" in df else [0]*len(x)
            y2 = df["MQ135"].fillna(0) if "MQ135" in df else [0]*len(x)
            y3 = df["Temp"].fillna(0) if "Temp" in df else [0]*len(x)
            y4 = df["Hum"].fillna(0) if "Hum" in df else [0]*len(x)


            return {
                "Timestamps": x.to_list(),
                "MQ7": y1.to_list(),
                "MQ135": y2.to_list(),
                "Temp": y3.to_list(),
                "Hum": y4.to_list()
            }
            