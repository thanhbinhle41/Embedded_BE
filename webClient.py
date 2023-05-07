import time, random, json

from paho.mqtt import client as mqtt_client

from arduinoClient2 import ArduinoClient2


class WebClient:
    def __init__(self):
        self.BROKER = 'broker.emqx.io'
        self.PORT = 8084
        self.TOPIC = "web_arduino_client_topic"
        # generate client ID with pub prefix randomly
        self.CLIENT_ID = "python-mqtt-ws-pub-sub-{id}".format(
            id=random.randint(0, 1000))
        self.USERNAME = 'emqx'
        self.PASSWORD = 'public'
        self.FLAG_CONNECTED = 0

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.FLAG_CONNECTED = 1
            print("Connected to MQTT Broker Web Client!")
            client.subscribe(self.TOPIC)
        else:
            print("Failed to connect, return code {rc}".format(rc=rc), )

    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode()
        topic = msg.topic
        new_payload = json.loads(payload)
        self.callbackWebClient(new_payload)
        
    def connect_mqtt(self):
        client = mqtt_client.Client(self.CLIENT_ID, transport='websockets')
        client.username_pw_set(self.USERNAME, self.PASSWORD)
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.tls_set()
        client.connect(self.BROKER, self.PORT)
        return client

    def callbackWebClient(self, payload):
        if payload["type"] == "measure_sequence":
            ArduinoClient2().publish(self.arduinoClient2, "Analog=0")
        elif payload["type"] == "measure_continuous":
            isSendDataContinuous = True
    
        if payload["type"] == "turn_on":
            device = payload["device"]
            ArduinoClient2().publish(self.arduinoClient2, f"{device}=on")
        elif payload["type"] == "turn_off":
            device = payload["device"]
            ArduinoClient2().publish(self.arduinoClient2, f"{device}=off")

            
    def publish(self, client, msg):
        client.publish(self.TOPIC, msg)

    def run(self):
        self.arduinoClient2 = ArduinoClient2().connect_mqtt()
        self.arduinoClient2.loop_start()
        time.sleep(1)
        
        webClient = self.connect_mqtt()
        webClient.loop_start()
        time.sleep(1)
        
        return webClient
