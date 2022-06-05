#if defined(ESP32)
#include <WiFiMulti.h>
WiFiMulti wifiMulti;
#define DEVICE "ESP32"
#elif defined(ESP8266)
#include <ESP8266WiFiMulti.h>
ESP8266WiFiMulti wifiMulti;
#define DEVICE "ESP8266"
#endif

#include <InfluxDbClient.h>
#include <InfluxDbCloud.h>


#include <WiFi.h>
#include "time.h"

#include <Adafruit_GFX.h>
#include <Adafruit_ST7735.h>
#include <Adafruit_ST7789.h>
#include <SPI.h>

#define WIFI_SSID "IIIP"
#define WIFI_PASSWORD "ME310Printer"
#define INFLUXDB_URL "https://us-west-2-2.aws.cloud2.influxdata.com"
#define INFLUXDB_TOKEN "17P7H-YsLvzfDRbJvrU_oStYwusEiviL0XZajw3gIzd0RMhJRlbqOemoqBeqB3r54K9Z3QwRMecTa489n3lO4Q=="
#define INFLUXDB_ORG "luisjdo@stanford.edu"
#define INFLUXDB_BUCKET "GSRSensor"

#define TZ_INFO "CET-1CEST,M3.5.0,M10.5.0/3"

InfluxDBClient client(INFLUXDB_URL, INFLUXDB_ORG, INFLUXDB_BUCKET, INFLUXDB_TOKEN, InfluxDbCloud2CACert);

Point sensor("wifi_status");

const int GSR=34;
int sensorValue=0;
int gsr_average=0;

const char* ntpServer = "pool.ntp.org";
const long  gmtOffset_sec = -8*3600;
const int   daylightOffset_sec = 1*3600;

// ESP32-Mini Display 
#define TFT_SCLK       4
#define TFT_MOSI       12
#define TFT_CS         32
#define TFT_RST        25 // Or set to -1 and connect to Arduino RESET pin
#define TFT_DC         27

Adafruit_ST7789 tft = Adafruit_ST7789(TFT_CS, TFT_DC, TFT_MOSI, TFT_SCLK, TFT_RST);

int _hour;
int _min = -1;
bool _updateTime = true;

float h = 1.0f;
float t = 2.0f;


void getLocalTime()
{
  struct tm timeinfo;
  if(!getLocalTime(&timeinfo)){
    Serial.println("Failed to obtain time");
    _hour = 10;
    _min = 15;
    return;
  }
  _hour = timeinfo.tm_hour;
  if (_min != timeinfo.tm_min){
    _updateTime = true;
  }
  else {
    _updateTime = false;
  }
  _min = timeinfo.tm_min;
}


void setup() {
  Serial.begin(115200);

  WiFi.mode(WIFI_STA);
  wifiMulti.addAP(WIFI_SSID, WIFI_PASSWORD);

  Serial.print("Connecting to wifi");
  while (wifiMulti.run() != WL_CONNECTED) {
    Serial.print(".");
    delay(100);
  }
  Serial.println();

  sensor.addTag("device", DEVICE);
  sensor.addTag("SSID", WiFi.SSID());

  timeSync(TZ_INFO, "pool.ntp.org", "time.nis.gov");

  if (client.validateConnection()) {
    Serial.print("Connected to InfluxDB: ");
    Serial.println(client.getServerUrl());
  } else {
    Serial.print("InfluxDB connection failed: ");
    Serial.println(client.getLastErrorMessage());
  }

  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
  getLocalTime();

  tft.init(240, 240);
  tft.fillScreen(ST77XX_BLACK);
}


void loop() {
  long sum=0;

  for(int i=0;i<10;i++)
  {
    sensorValue=analogRead(GSR);
    sum += sensorValue;
    delay(5);
  }
  gsr_average = sum/10;

   Serial.println(gsr_average);
  
  sensor.clearFields();
  sensor.addField("gsr_average", gsr_average);

  Serial.print("Writing: ");
  Serial.println(sensor.toLineProtocol());

  if (wifiMulti.run() != WL_CONNECTED) {
    Serial.println("Wifi connection lost");
  }

  if (!client.writePoint(sensor)) {
    Serial.print("InfluxDB write failed: ");
    Serial.println(client.getLastErrorMessage());
  }

  Serial.println("Wait 10s");
  delay(1000);

  getLocalTime();
  if (_updateTime) {
    updateDisplayWithTime(); 
  }
}

void updateDisplayWithTime() {
  tft.fillScreen(ST77XX_BLACK);
  tft.setCursor(0, 0);
  tft.setTextColor(ST77XX_GREEN);
  tft.setTextSize(4);
  tft.println("Thu 02 Jun");
  tft.println("");
  tft.setTextColor(ST77XX_BLUE);
  tft.setTextSize(8);
  tft.println("");
  String watchTime = "";
  if (_hour < 10) {
    watchTime = watchTime + "0";
  }
  watchTime = watchTime + _hour;
  watchTime = watchTime + ":";
  if (_min < 10) {
    watchTime = watchTime + "0";
  }
  watchTime = watchTime + _min;
  tft.println(watchTime);
}
