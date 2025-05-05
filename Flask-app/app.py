import os
import re
import threading
import http.client
import requests
import json

from flask import Flask, jsonify, request
from flask_cors import CORS

from dotenv import load_dotenv
from pathlib import Path

from fire_inference import Fire_Inference
from llm_invoking import LLM_Invoking
from mqtt import MQTT
from location import Location
from db import DB

load_dotenv(dotenv_path=Path('.env'))

app = Flask(__name__)
CORS(app)

fire_detector = Fire_Inference()
chatbot = LLM_Invoking()
mqtt = MQTT(fire_detector)
location = Location()
db = DB()

camera_thread = threading.Thread(target=fire_detector.camera, daemon=True)
mqtt_thread = threading.Thread(target=mqtt.start, daemon=True)
# print("FLASK APP INITIALIZED")

@app.route('/api/vision', methods=['GET'])
def vision():
    try:
        yaw, pitch = fire_detector.inference()

        # Call
        requests.get("http://127.0.0.1:5000/api/call")

        return jsonify({
            "yaw": yaw,
            "pitch": pitch
        }), 200
    
    except Exception as e:
        print(f"Error happened on server side: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/api/llm', methods=['POST'])
def llm():
    try:
        body = request.get_json()
        data = body['input_text']
        print(data)

        rag_state = chatbot.is_rag_needed(data)
        print("RAG State: ", rag_state)

        key_and_metadata = {
            "air": "Air-Quality-Factors",
            "fire": "How Fire Incidents Happen",
            "bombatronic": "Bombatronic - Dataset"
        }

        input_metadata = [md for key, md in key_and_metadata.items() if re.search(key, data.lower())]
        print("Metadata: ", input_metadata)

        response = chatbot.chatbot_response(data, rag_state, input_metadata)
        return jsonify({"answer": response}), 200

    except Exception as e:
        print(f"Error happened on server side: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/api/call', methods=["GET"])
def call():
    try:
        address = location.get_location()

        conn = http.client.HTTPSConnection("8kq6x9.api.infobip.com")
        payload = json.dumps({
            "messages": [
                {
                    "destinations": [{"to":f'{os.getenv("PHONE_NUMBER")}'}],
                    "from": "38515507799",
                    "language": "id",
                    "text": f"Api terdeteksi di {address}",
                }
            ]
        })
        headers = {
            'Authorization': f'App {os.getenv("INFOBIP_AUTH")}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        conn.request("POST", "/tts/3/advanced", payload, headers)
        res = conn.getresponse()
        data = res.read().decode('utf-8')

        return jsonify({
            "address": f"{address}",
            "data": data
        }), 200
    except Exception as e:
        print(f"Error happened on server side: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/api/fetch_db', methods=["GET"])
def fetch_db():
    current_dict = db.fetch_db()
    if "Error" in current_dict:
        return jsonify(current_dict), 500
    else:
        print(current_dict)
        return jsonify(current_dict), 200

# if __name__ == "__main__":
mqtt_thread.start()
camera_thread.start()
    # app.run(host="0.0.0.0", port=5000, debug=True)
