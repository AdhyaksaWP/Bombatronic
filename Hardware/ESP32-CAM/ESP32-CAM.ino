#include <WiFi.h>
#include <esp32cam.h>
#include <WebServer.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// WiFi Credentials
const char* ssid = "UGM eduroam";
const char* password = "moyf7667";

// MQTT Configuration
const char* mqtt_broker = "broker.emqx.io";
const char* mqtt_client_id = "sic6_cam_module";
const char* mqtt_topic_pub_cam = "/UNI544/ADHYAKSAWARUNAPUTRO/cam_url";

WiFiClient espClient;
PubSubClient client(espClient);
WebServer server(80);

// Set resolution to 320x240
static auto loRes = esp32cam::Resolution::find(320, 240);

unsigned long lastPublishTime = 0;

void serveJpg()
{
  auto frame = esp32cam::capture();
  if (frame == nullptr) {
    server.send(503, "", "");
    return;
  }
  server.setContentLength(frame->size());
  server.send(200, "image/jpeg");
  WiFiClient client = server.client();
  frame->writeTo(client);
}

void handleCam()
{
  esp32cam::Camera.changeResolution(loRes);
  serveJpg();
}

void setupWiFi() {
  Serial.print("Connecting to WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("Connected to WiFi!");
  Serial.println(WiFi.localIP());
}

void setupMQTT() {
  client.setServer(mqtt_broker, 1883);
  while (!client.connected()) {
    Serial.print("Connecting to MQTT...");
    if (client.connect(mqtt_client_id)) {
      // Serial.println("Connected to MQTT!");
    } else {
      Serial.print("Failed, rc=");
      Serial.print(client.state());
      Serial.println(" Trying again in 5 seconds...");
      delay(5000);
    }
  }
}

void publishCamUrl() {
  DynamicJsonDocument doc(256);
  String url = "http://" + WiFi.localIP().toString() + "/cam-lo.jpg";
  doc["url"] = url;

  char payload[256];
  serializeJson(doc, payload);
  client.publish(mqtt_topic_pub_cam, payload);
}

void setup() {
  Serial.begin(115200);

  {
    using namespace esp32cam;
    Config cfg;
    cfg.setPins(pins::AiThinker);
    cfg.setResolution(loRes); // Use 320x240 resolution
    cfg.setBufferCount(2);
    cfg.setJpeg(80);

    if (!Camera.begin(cfg)) {
      Serial.println("CAMERA INIT FAIL");
      while (1);
    }
  }

  setupWiFi();
  setupMQTT();

  server.on("/cam-lo.jpg", handleCam);
  server.begin();

  publishCamUrl(); // Publish once at boot
}

void loop() {
  if (!client.connected()) {
    setupMQTT();
  }
  client.loop();
  server.handleClient();

  // Optional: Re-publish URL every 10 seconds
  if (millis() - lastPublishTime > 10000) {
    publishCamUrl();
    lastPublishTime = millis();
  }
}
