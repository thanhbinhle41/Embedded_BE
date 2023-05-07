import random

from paho.mqtt import client as mqtt_client


class ArduinoClient2:
    def __init__(self):
        self.BROKER = 'broker.hivemq.com'
        self.PORT = 1883
        self.TOPIC_GET = "enviroment/capture"
        self.TOPIC_POST = "device/update_status"
        # generate client ID with pub prefix randomly
        self.CLIENT_ID = "python-mqtt-{id}".format(
            id=random.randint(0, 10000))
        self.USERNAME = 'emqx123'
        self.PASSWORD = 'public'
        

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.FLAG_CONNECTED = 1
            print("Connected to MQTT Broker Arduino Client 2!")
            client.subscribe(self.TOPIC_GET)
            client.subscribe(self.TOPIC_POST)
        else:
            print("Failed to connect, return code {rc}".format(rc=rc))

    def connect_mqtt(self):
        client = mqtt_client.Client(self.CLIENT_ID)
        client.username_pw_set(self.USERNAME, self.PASSWORD)
        client.on_connect = self.on_connect
        client.connect(self.BROKER, self.PORT)
        return client
    
    def publish(self, client, msg):
        client.publish(self.TOPIC_POST, msg)
        
        
