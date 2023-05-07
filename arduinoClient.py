import time, random, json

from paho.mqtt import client as mqtt_client
from webClient import WebClient


class ArduinoClient:
    def __init__(self):
        self.BROKER = 'broker.hivemq.com'
        self.PORT = 1883
        self.TOPIC_GET = "enviroment/capture"
        self.TOPIC_POST = "device/update_status"
        # generate client ID with pub prefix randomly
        self.CLIENT_ID = "python-mqtt-ws-pub-sub-{id}".format(
            id=random.randint(0, 1000))
        self.USERNAME = 'emqx123'
        self.PASSWORD = 'public'
        self.FLAG_CONNECTED = 0
        self.arduinoClient = None
        

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.FLAG_CONNECTED = 1
            print("Connected to MQTT Broker Arduino Client!")
            client.subscribe(self.TOPIC_GET)
            client.subscribe(self.TOPIC_POST)
        else:
            print("Failed to connect, return code {rc}".format(rc=rc), )

    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode()
        topic = msg.topic
        print(payload)
        if topic != self.TOPIC_GET:
            return
        self.callbackArduinoClient(payload)

    def connect_mqtt(self):
        client = mqtt_client.Client(self.CLIENT_ID)
        client.username_pw_set(self.USERNAME, self.PASSWORD)
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.connect(self.BROKER, self.PORT)
        return client

    

    def publish(self, client, msg):
        client.publish(self.TOPIC_POST, msg)
        
    def stay_online(self):
        while True:
            print("Online")
            time.sleep(100)
            
    def callbackArduinoClient(self, msg):
        print(msg, "in call back")
        if "humidity" in msg and "light" in msg and "sound" in msg:
            data = msg.split("|")
            humidity = data[0].split("=")[1]
            light = data[1].split("=")[1]
            sound = data[2].split("=")[1]

            # HANDLE HUMIDITY
            if int(humidity) > 100:
                self.publish(self.arduinoClient, "Pump=on")
            elif int(humidity) > 200:
                self.publish(self.arduinoClient, "Pump=off")

            # HANDLE LIGHT
            if int(light) > 100:
                self.publish(self.arduinoClient, "Light=on")
            elif int(light) > 200:
                self.publish(self.arduinoClient, "Light=off")

            # HANDLE SOUND
            if int(sound) > 100:
                self.publish(self.arduinoClient, "Servo=on")
            elif int(sound) > 200:
                self.publish(self.arduinoClient, "Servo=off")

            if isSendDataContinuous:
                tmpData = {
                    "type": "continuous",
                    "humidity": humidity,
                    "light": light,
                    "sound": sound
                }
                dataPublish = json.dumps(tmpData)
                isSendDataContinuous = False
                WebClient().publish(self.webClient, dataPublish)

        else:
            data = msg.split("|")
            temperature = data[0].split("=")[1]
            air_humidity = data[1].split("=")[1]
            water = data[2].split("=")[1]
            tmpData = {
                "type": "sequence",
                "hutemperaturemidity": temperature,
                "air_humidity": air_humidity,
                "water": water
            }
            dataPublish = json.dumps(tmpData)
            print(dataPublish, self.webClient)
            WebClient().publish(self.webClient, dataPublish)
            
    

    def run(self):
        self.webClient = WebClient().run()
        self.webClient.loop_start()
        time.sleep(1)
        
        self.arduinoClient = self.connect_mqtt()
        self.arduinoClient.loop_start()
        time.sleep(1)
        
        if self.FLAG_CONNECTED:
            self.stay_online()
        else:
            self.arduinoClient.loop_stop()
            self.webClient.loop_stop()
        
