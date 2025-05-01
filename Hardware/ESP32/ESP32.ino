#include <Wire.h>
#include <Adafruit_ADS1X15.h>
#include <DHT.h>
#include <ESP32Servo.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// DHT 11 Setup
#define DHTPIN 23
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// WiFi Credentials
const char* ssid = "UGM eduroam";
const char* password = "moyf7667";

// MQTT Configuration
const char*  mqtt_broker = "broker.emqx.io";
const char*  mqtt_client_id = "sic6_prototype_esp32";
const char*  mqtt_topic_pub = "/UNI544/ADHYAKSAWARUNAPUTRO/data_sensor";
const char*  mqtt_topic_pub_cam = "/UNI544/ADHYAKSAWARUNAPUTRO/cam_url";
const char*  mqtt_topic_sub = "/UNI544/ADHYAKSAWARUNAPUTRO/servo_angles";

WiFiClient espClient; // Initialize Client for WiFi
PubSubClient client(espClient); // Initialize client for MQTT

// Servo setup
Servo servoYaw;
Servo servoPitch;
const int 
SERVO_YAW_PIN = 2,
SERVO_PITCH_PIN = 15;

// ADS1115 setup
Adafruit_ADS1115 ads;

// UART communication setup
const int 
UART_RX_PIN = 16, 
UART_TX_PIN = 17;

// Sensor Thresholds
const float
THRESHOLD_FIRE = 5000,
THRESHOLD_MQ135 = 3000,
THRESHOLD_MQ7 = 3000,
THRESHOLD_TEMPERATURE = 40.0;

const int RELAY_PIN = 5;
bool fireTrigerred = false;

uint8_t 
cur_yaw = 90, 
cur_pitch = 90, 
prev_yaw = cur_yaw,
prev_pitch = cur_pitch;

// Function to connect to WiFi
void setupWiFi() {
  Serial.print("Connecting to WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("Connected to WiFi!");
}

// Function to connect to MQTT broker
void setupMQTT() {
  client.setServer(mqtt_broker, 1883);
  client.setCallback(callback);

  while (!client.connected()) {
    Serial.print("Connecting to MQTT...");
    if (client.connect(mqtt_client_id)) {
      client.subscribe(mqtt_topic_sub);
      Serial.println("Connected to MQTT!");
    } else {
      Serial.print("Failed, rc=");
      Serial.print(client.state());
      Serial.println(" Trying again in 5 seconds...");
      delay(5000);
    }
  }
}

// Callback function for client subscribe
void callback (char* topic, byte* payload, unsigned int length) {
  
  if (String(topic) == mqtt_topic_sub) {
    DynamicJsonDocument doc(1024);
    DeserializationError error = deserializeJson(doc, payload, length);
    
    if (error) {
      Serial.print("deserializeJson() failed: ");
      Serial.println(error.f_str());
      return;
    }

    // Ensure "yaw" and "pitch" keys exist
    if (doc.containsKey("yaw") && doc.containsKey("pitch")) {
      cur_yaw = doc["yaw"];
      cur_pitch = doc["pitch"];

      // // Check if the data is valid or not by sending back into the publisher topic
      // DynamicJsonDocument PubDoc(256);
      // PubDoc["yaw"] = cur_yaw;
      // PubDoc["pitch"]= cur_pitch;
      // char pubPayload[1024];

      // serializeJson(PubDoc, pubPayload);
      // client.publish(mqtt_topic_pub, pubPayload);

      // Serial.print("YAW: "); Serial.print(cur_yaw);
      // Serial.print(" , PITCH: "); Serial.println(cur_pitch);
    } else {
      Serial.println("Invalid JSON format: missing yaw or pitch");
    }
  }
}

// Function to read sensors and publish data
void readSensors() {
  int sensorMQ7 = ads.readADC_SingleEnded(1);
  int sensorMQ135 = ads.readADC_SingleEnded(2);
  int sensorProximity = ads.readADC_SingleEnded(3);
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  
  Serial.print("MQ7: "); Serial.print(sensorMQ7);
  Serial.print(" | MQ135: "); Serial.print(sensorMQ135);
  Serial.print(" | IR: "); Serial.print(sensorProximity);
  Serial.print(" | Suhu: "); Serial.println(temperature);
  
  fireTrigerred = (sensorProximity < THRESHOLD_FIRE || (sensorMQ135 < THRESHOLD_MQ135 &&
                   sensorMQ7 < THRESHOLD_MQ7 && temperature > THRESHOLD_TEMPERATURE));
  
  DynamicJsonDocument sensDoc(1024);
  sensDoc["MQ7"] = sensorMQ7;
  sensDoc["MQ135"] = sensorMQ135;
  sensDoc["IR"] = sensorProximity;
  sensDoc["Temp"] = temperature;
  sensDoc["Hum"] = humidity;
  sensDoc["status"] = fireTrigerred ? 1 : 0;

  char payload[150];
  serializeJson(sensDoc, payload);

  // snprintf(payload, sizeof(payload), "{\"MQ7\":%d,\"MQ135\":%d,\"IR\":%d,\"Temp\":%.2f,\"status\":\"%d\"}",
          // sensorMQ7, sensorMQ135, sensorProximity, temperature, fireTriggered ? 1 : 0);
  // snprintf(payload, sizeof(payload), "{\"MQ7\":%d,\"MQ135\":%d,\"IR\":%d,\"Temp\":%.2f,\"status\":\"%d\"}",
  //       sensorMQ7, sensorMQ135, sensorProximity, temperature, 1);
  client.publish(mqtt_topic_pub, payload);
}

void sendUrl() {
  if (Serial2.available() > 0) {
    String url = Serial2.readStringUntil('\n');

    DynamicJsonDocument urlDoc(256);
    urlDoc["url"] = url;

    char urlPayload[256];
    serializeJson(urlDoc, urlPayload);  

    client.publish(mqtt_topic_pub_cam, urlPayload);
  }
}


void setup() {
  Serial.begin(115200);
  Serial2.begin(9600, SERIAL_8N1, UART_RX_PIN, UART_TX_PIN);

  Wire.begin();
  ads.begin();
  dht.begin();

  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, HIGH);

  servoYaw.attach(SERVO_YAW_PIN);
  servoPitch.attach(SERVO_PITCH_PIN);

  servoYaw.write(90);
  servoPitch.write(150);
  
  setupWiFi();
  setupMQTT();
  Serial.println("Sistem Bombatronic siap");
}

void loop() {
  if (!client.connected()) {
    setupMQTT();
  }
  client.loop();
  readSensors();
  sendUrl();
  
  if ((cur_yaw != prev_yaw) || (cur_pitch != prev_pitch)){
    servoYaw.write(cur_yaw);
    servoPitch.write(cur_pitch);
    delay(500);
    digitalWrite(RELAY_PIN, LOW);
    delay(2000);
  }
  else {
    digitalWrite(RELAY_PIN, HIGH);
    delay(500);
  }

  prev_yaw = cur_yaw;
  prev_pitch = cur_pitch;
  delay(1000); // Publish every second
}
