import paho.mqtt.client as mqtt
import time

MQTT_SERVER = "192.168.0.12"
MQTT_PATH = "MoodLight/#"

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(MQTT_PATH)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    message=str(msg.payload)
    topic = msg.topic
    print(topic+" "+message)
    if(topic=="MoodLight/Color"):
        print("Color Changed")
        red = int('0x'+message[4:6],16)
        green =int('0x'+message[6:8],16)
        blue = int('0x'+message[8:10],16)
        print(red,green,blue)

    if(topic == "MoodLight/Mode"):
        print("Mode change")
        LightMode = message[2:-1]
        #print(LightMode)
        if(LightMode == 'ColorWipe'):
            print("CW")
        elif(LightMode == 'TheaterChase'):
            print('TC')
        elif(LightMode == 'Rainbow'):
            print("RB")
        else:
            print("Unknown Mode")


    if(topic == "MoodLight/Power"):
        print("power changed")
        PowerMode = message[2:-1]
        if(PowerMode == 'on'):
            print('on')
        elif(PowerMode == 'off'):
            print('off')
    # more callbacks, etc

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_SERVER, 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.

client.loop_start();