import paho.mqtt.client as mqtt
import time

def on_connect(client, userdata, flags, rc):
    if rc==0:
        client.connected_flag=True
        print("Connected OK")
    else:
        print("Bad connect: ", rc)
    
broker = "127.0.0.1"
port = 1883
client = mqtt.Client("python1")
client.on_connect=on_connect
client.connect(broker, port)
client.loop_start()
while not client.connected_flag:
    print("Waiting to connect...")
    time.sleep(1)
client.publish("/things/python1/value", "test1")
time.sleep(4)
client.loop_stop()
client.disconnect()
