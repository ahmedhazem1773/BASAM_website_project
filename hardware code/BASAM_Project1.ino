/*********
  Rui Santos & Sara Santos - Random Nerd Tutorials
  Complete instructions at https://RandomNerdTutorials.com/esp32-firebase-realtime-database/
*********/
#define ENABLE_USER_AUTH
#define ENABLE_DATABASE

#include <DHT.h>
#include <DHT_U.h>

DHT dht(26, DHT22);

#define soil_moisture_pin 34

#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <FirebaseClient.h>
#include <WiFiManager.h>   // WifiManager library
WiFiManager wm;           

#define Web_API_KEY "Web_API_KEY"
#define DATABASE_URL "DATABASE_URL"
#define USER_EMAIL "USER_EMAIL"
#define USER_PASS "USER_PASS"

String SERIAL_NUMBER  ;      //serial number

// User function
void processData(AsyncResult &aResult);

// Authentication
UserAuth user_auth(Web_API_KEY, USER_EMAIL, USER_PASS);

// Firebase components
FirebaseApp app;
WiFiClientSecure ssl_client;
using AsyncClient = AsyncClientClass;
AsyncClient aClient(ssl_client);
RealtimeDatabase Database;

// Timer variables for sending data every 10 seconds
unsigned long lastSendTime = 0;
const unsigned long sendInterval = 10000; // 10 seconds in milliseconds

unsigned long previousMillis = 0;  //.........
const long interval = 2000;        // time between every read

float humidity;
float temp;
int soilValue;
int moisturePercent;

int dryThreshold = 3000 ;     //pump
int wetThreshold = 2600 ;     //pump
   

void setup(){
  Serial.begin(115200);

  delay(1000);
  Serial.println("Starting ESP32...");

  // The duration the access point mode remains open (in seconds)
  wm.setConfigPortalTimeout(180);  // 3 minutes

  // Try to connect to the saved network
  // If it fails , open access point (ESP32_Config1)
  bool connected = wm.autoConnect("ESP32_Config1","khalaf_3mk");

 // restart if not connected after timeout
  if (!connected) {
    Serial.println("Failed to connect. Restarting...");
    delay(3000);
    ESP.restart();
  }
 // if connected
  Serial.println("WiFi Connected!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
   
   //Get SERIAL_NUMBER from esp32
  uint64_t chipid = ESP.getEfuseMac();
 char serial[20];
 sprintf(serial, "ESP32_%04X", (uint16_t)(chipid>>32));
 SERIAL_NUMBER = String(serial);

 Serial.print("Device Serial Number: ");
 Serial.println(SERIAL_NUMBER);

  dht.begin(); // for dht
  
  pinMode(soil_moisture_pin , INPUT); // moisture pin type

  pinMode(18, OUTPUT_OPEN_DRAIN);     //PUMP
  
  // Configure SSL client
  ssl_client.setInsecure();
  ssl_client.setTimeout(1000);
  ssl_client.setHandshakeTimeout(5);
  
  // Initialize Firebase
  initializeApp(aClient, app, getAuth(user_auth), processData, "🔐 authTask");
  app.getApp<RealtimeDatabase>(Database);
  Database.url(DATABASE_URL);
}

void loop(){
   // Maintain authentication and async tasks
  app.loop();

 unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;

      temp = dht.readTemperature();     // Reading Temperature
   humidity = dht.readHumidity();       // Reading Humidity
  Serial.print("Temp: ");
  Serial.print(temp);
  Serial.print(" C ");
  Serial.print("Humidity: ");
  Serial.print(humidity);
  Serial.print(" % ");
 
  soilValue = analogRead(soil_moisture_pin);     // Reading soil humidity
   moisturePercent = map(soilValue,4095,1072,0,100);
   moisturePercent = constrain(moisturePercent,0,100);
  Serial.print("soilValue: ");
  Serial.println(soilValue);

  Serial.print(" Moisture: ");
  Serial.print(moisturePercent);
  Serial.println("%");

  if(soilValue > dryThreshold  ){    //PUMP on
   digitalWrite(18, LOW);
    Serial.println("PUMP ON");
  }
  if(soilValue < wetThreshold ){       //PUMP off
    digitalWrite(18, HIGH);
    Serial.println("PUMP OFF");
  }

  Serial.println("-------------------------");

  }

  // Check if authentication is ready
  if (app.ready()){ 
    // Periodic data sending every 10 seconds
     unsigned long currentTime = millis();
    if (currentTime - lastSendTime >= sendInterval){
      // Update the last send time
      lastSendTime = currentTime;
      
      // sending values to firebase
      String basePath = "/devices/" + SERIAL_NUMBER;
     Database.set<float>(aClient, basePath + "/humidity", humidity, processData, "RTDB_Send_Float");
     Database.set<float>(aClient, basePath + "/moisture", moisturePercent, processData, "RTDB_Send_Float");
     Database.set<float>(aClient, basePath + "/temperature", temp, processData, "RTDB_Send_Float");
     // send SERIAL_NUMBER
     Database.set<String>(aClient, basePath + "/SERIAL_NUMBER", SERIAL_NUMBER, processData, "RTDB_Send_String");
    }
  }
}

void processData(AsyncResult &aResult) {
  if (!aResult.isResult())
    return;

  if (aResult.isEvent())
    Firebase.printf("Event task: %s, msg: %s, code: %d\n", aResult.uid().c_str(), aResult.eventLog().message().c_str(), aResult.eventLog().code());

  if (aResult.isDebug())
    Firebase.printf("Debug task: %s, msg: %s\n", aResult.uid().c_str(), aResult.debug().c_str());

  if (aResult.isError())
    Firebase.printf("Error task: %s, msg: %s, code: %d\n", aResult.uid().c_str(), aResult.error().message().c_str(), aResult.error().code());

  if (aResult.available())
    Firebase.printf("task: %s, payload: %s\n", aResult.uid().c_str(), aResult.c_str());
}

