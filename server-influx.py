#script to read the mqtt feed and put it into a local influx db. 

import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient
from line_protocol_parser import parse_line
import json

broker="localhost"
port=1883
mqtt_ok=0

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
    #current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #json_body = [
    #{
    #    "measurement": "temperature",
    #    "tags": {
    #        "host": "aquarium",
    #    },
    #  #  "time": str(current_time),
    #    "fields": {
    #        "value": str(msg.payload)
    #    }
    #}
    #]
    #influx_client.write_points(json_body)
    #print(msg.topic+" "+str(msg.payload))
    
    datastring = msg.payload.decode("utf-8") 
    datastring = datastring.strip("[']")
    print(datastring)
    print(msg.topic)
    cosmicdict = parse_line(datastring)
    #json_object = json.dumps(data_sub, indent=4)
    #json_object = str(data_sub)
    #addtodb = "["+"\r\n"+str(json_object)+"\r\n"+"]"
    if msg.topic == "cosmicpi/1.8.1":
        data = []
        data.append("{measurement},id={DeviceID} lat={latitude},lon={longitude},Temp={Temp},Hum={Hum},Accelx={Accelx},Accely={Accely},Accelz={Accelz},Magx={Magx},Magy={Magy},Magz={Magz},Press={Pressx},Alt={Altx} {timestamp}"
            .format(measurement='CosmicPiV1.8.1',
                    DeviceID=cosmicdict['tags']['id'],
                    latitude=cosmicdict['fields']['lat'],
                    longitude=cosmicdict['fields']['lon'],
                    Temp=cosmicdict['fields']['Temp'],
                    Hum=cosmicdict['fields']['Hum'],
                    Accelx=cosmicdict['fields']['Accelx'],
                    Accely=cosmicdict['fields']['Accely'],
                    Accelz=cosmicdict['fields']['Accelz'],
                    Magx=cosmicdict['fields']['Magx'],
                    Magy=cosmicdict['fields']['Magy'],
                    Magz=cosmicdict['fields']['Magz'],
                    Pressx=cosmicdict['fields']['Press'],
                    Altx=cosmicdict['fields']['Alt'],
                    timestamp=cosmicdict['time']))
        influx_client.write_points(data, time_precision='n', batch_size=1, protocol='line')
        #influx_client.write(addtodb)
        print("wrote event")
    if msg.topic == "cosmicpi/worldmap":
        data = []
        data.append("{measurement},id={DeviceID} geohash={geohash_pos},event_count={event_count} {timestamp}"
            .format(measurement='CosmicPiV1.8.1_freq',
                    DeviceID=cosmicdict['tags']['id'],
                    geohash_pos="\""+cosmicdict['fields']['geohash']+"\"",
                    event_count=cosmicdict['fields']['event_count'],
                    timestamp=cosmicdict['time']))
        influx_client.write_points(data, time_precision='s', batch_size=1, protocol='line')
        print("wrote mappoint")

client1= mqtt.Client("master")
#client1.on_publish = on_publish

client1.username_pw_set(username="cosmicpi",password="MuonsFROMSp8ce")
client1.on_connect=on_connect #binding call

influx_client = InfluxDBClient(host='localhost', port=8086, database='cosmicpiglobal')

client1.on_message = on_message

client1.connect("localhost", 1883, 60)


# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client1.loop_forever()
