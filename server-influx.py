#script to read the mqtt feed and put it into a local influx db. 

import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient

broker="cosmicpidata.mooo.com"
port=1883
mqtt_ok=0

def on_publish(client,userdata,result):
    print("Data published to MQTT server")
    pass


def on_connect(client,userdata,flags,rc):
    if rc==0:
        print("connected ok")
    else:
        print("mqtt connection failed")
    client.subscribe("cosmicpi/worldmap/#")
    client.subscribe("cosmicpi/1.8.1/#")
    
# The callback for when a PUBLISH message is received from the server.
#fix this up later
def on_message(client, userdata, msg):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    json_body = [
    {
        "measurement": "temperature",
        "tags": {
            "host": "aquarium",
        },
      #  "time": str(current_time),
        "fields": {
            "value": str(msg.payload)
        }
    }
    ]
    influx_client.write_points(json_body)
    print(msg.topic+" "+str(msg.payload))

client1= mqtt.Client("control1")
client1.on_publish = on_publish

client1.username_pw_set(username="cosmicpi",password="MuonsFROMSp8ce")
client1.on_connect=on_connect #binding call

influx_client = InfluxDBClient('localhost', 8086, database='cosmicpi')
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("cosmicpidata.mooo.com", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
