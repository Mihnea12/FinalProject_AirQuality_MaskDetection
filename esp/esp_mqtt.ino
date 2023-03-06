#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <NTPClient.h>
#include <WiFiUdp.h>

// WiFi
const char *ssid = "wfSerban"; // Enter your WiFi name
const char *password = "Serb@n_P@$cu";  // Enter WiFi password

// MQTT Broker
const char *mqtt_broker = "broker.emqx.io";
const char *ppm_topic = "mihnea/ppm";
const char *aqi_topic = "mihnea/aqi";
const char *time_topic = "mihnea/time";
const char *mqtt_username = "emqx";
const char *mqtt_password = "public";
const int mqtt_port = 1883;

const long utcOffsetInSeconds = 7200;

WiFiClient espClient;
PubSubClient client(espClient);
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org", utcOffsetInSeconds);

#define anInput     A0                        //analog feed from MQ135
#define co2Zero     80                        //calibrated CO2 0 level
#define csPin       D8                     
#include <SPI.h>
#include <SD.h>
File myFile_ppm;
File myFile_aqi;

void setup() {
  // Set software serial baud to 9600;
  Serial.begin(9600);
  // connecting to a WiFi network
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.println("Connecting to WiFi..");
  }
  Serial.println("Connected to the WiFi network");
  //connecting to a mqtt broker
  client.setServer(mqtt_broker, mqtt_port);
  client.setCallback(callback);
  while (!client.connected()) {
      String client_id = "esp8266-client-";
      client_id += String(WiFi.macAddress());
      Serial.printf("The client %s connects to the public mqtt broker\n", client_id.c_str());
      if (client.connect(client_id.c_str(), mqtt_username, mqtt_password)) {
          Serial.println("Public emqx mqtt broker connected");
      } else {
          Serial.print("failed with state ");
          Serial.print(client.state());
          delay(2000);
      }
  }

  timeClient.begin();

  pinMode(anInput,INPUT);                     //MQ135 analog feed set for input
  Serial.print("Initializing SD card...\n");
  if (!SD.begin(csPin)) {
  Serial.println("initialization failed!");
  while (1);
  }
  SD.remove("date_ppm.csv");
  SD.remove("date_aqi.csv");
  myFile_ppm = SD.open("date_ppm.csv", FILE_WRITE);
  myFile_aqi = SD.open("date_aqi.csv", FILE_WRITE);

//  client.subscribe(topic);
}

void callback(char *topic, byte *payload, unsigned int length) {
  Serial.print("Message arrived in topic: ");
  Serial.println(topic);
  Serial.print("Message:");
  for (int i = 0; i < length; i++) {
      Serial.print((char) payload[i]);
  }
  Serial.println();
  Serial.println("-----------------------");
}

void loop() { 
  timeClient.update();
  char buf[10];
  char *ptr;
  char cstr1[16],cstr2[16],cstr3[30];
  client.loop();

  int co2now[10];                               //int array for co2 readings
  int co2raw = 0;                               //int for raw value of co2
  int co2comp = 0;                              //int for compensated co2 
  int co2ppm = 0;                               //int for calculated ppm
  int zzz = 0;                                  //int for averaging
  int grafX = 0;                                //int for x value of graph
  int aqi = 0;

  String hour="";
  hour = String((timeClient.getHours()+1)%24);
  hour = hour + ":";
  hour = hour + String(timeClient.getMinutes());
  hour = hour + ":";
  hour = hour + String(timeClient.getSeconds());
  
  for (int x = 0;x<10;x++){                   //samplpe co2 10x over 2 seconds
    co2now[x]=analogRead(A0);
    delay(200);
  }
  
  for (int x = 0;x<10;x++){                     //add samples together
    zzz=zzz + co2now[x];
  }
  co2raw = zzz/40;                            //divide samples by 10
  co2comp = co2raw - co2Zero;
  aqi = co2comp;
  co2ppm = map(co2comp,0,1023,400,5000);      //map value for atmospheric levels
  Serial.print(co2ppm);
  Serial.print(",");
  Serial.print(aqi);
  Serial.print(",");
  Serial.println(hour);
  
  // if the file opened okay, write to it:
  if (myFile_ppm) {
    myFile_ppm.print(co2ppm);
    myFile_ppm.print(",");
    myFile_ppm.println(hour);
  } else {
    Serial.println("error opening myFile_ppm.txt");
  }

  if (myFile_aqi) {
    myFile_aqi.print(aqi);
    myFile_aqi.print(",");
    myFile_aqi.println(hour);
  } else {
    Serial.println("error opening myFile_aqi.txt");
  }
  itoa(co2ppm, cstr1, 10);
  itoa(aqi, cstr2, 10);
  hour.toCharArray(cstr3,30);
  client.publish(ppm_topic, cstr1);
  client.publish(aqi_topic, cstr2);
  client.publish(time_topic, cstr3);
  int time = millis();
  while(millis() - time < 20000){
    myFile_ppm.flush();
    myFile_aqi.flush();
    delay(0);
  }
  delay(50);
}  
