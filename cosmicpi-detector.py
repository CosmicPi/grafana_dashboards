from influxdb import InfluxDBClient
import requests
import serial
import geohash
import uuid
import random
import time
import datetime
import paho.mqtt.client as paho

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

mqttidentstring = str(uuid.getnode())
client1= paho.Client(mqttidentstring)
client1.on_publish = on_publish
client1.username_pw_set(username="cosmicpi",password="MuonsFROMSp8ce")
client1.on_connect=on_connect #binding call

url = "http://www.google.com"
timeout = 10

try:
    request = requests.get(url,timeout=timeout)
    print("internet ok")
    mqtt_ok=1
except (requests.ConnectionError, requests.Timeout) as exception:
    print("internet fail")
    mqtt_ok=0

dbframe = 0

cosmicdict = {
        "DeviceID": 0,
        "UTCUnixTime": 0,
        "SubSeconds": 0.0,
        "TemperatureC": 0.0,
        "Humidity": 0.0,
        "AccelX": 0.0,
        "AccelY": 0.0,
        "AccelZ": 0.0,
        "MagX": 0.0,
        "MagY": 0.0,
        "MagZ": 0.0,
        "Pressure": 0.0,
        "Altitude": 0.0,
        "Longitude": 0.0,
        "Latitude": 0.0
        }
        
nstimestamp = 0
geohash_pos = 0

eventcount = 0

print("starting")
ser = serial.Serial(port='/dev/serial0', baudrate=115200, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1)
print("connected to: " + ser.portstr)
print ("The device ID using uuid1() is : ",end="")
print (uuid.getnode())
cosmicdict['DeviceID']=uuid.getnode()

print("MQTT connection")
if mqtt_ok==1:
    client1.connect(broker,port)
#return 0

print("DB connection")
client = InfluxDBClient(host='localhost', port=8086)
client.create_database('cosmicpilocal')
data=[]

#ser.write("help\n");
while True:
    line = ser.readline();
    if line:
        #print(line.decode('utf-8'))
        line_str = str(line.decode('utf-8'))
        data_type = line_str.split(':')[0]
        gps_type = line_str.split(',')[0]
        #print(data_type)
        #print(gps_type)
        if data_type in cosmicdict.keys():
            data = line_str.split(':')[1].split(';')[0]
            cosmicdict[data_type] = float(data)
        if (data_type == "PPS"):
            print("found a pps")
            gps_lock_sting = line_str.split(':')[2]
            gps_lock_sting = gps_lock_sting.split(';')[0]
            if (len(gps_lock_sting) == 1):
                cosmicdict['UTCUnixTime'] += 1
        gps_type = line_str.split(',')[0]
        if gps_type == "$GPZDA" or gps_type == "$GNZDA":
            if (line_str.count(',') == 6):
                g_time_string = line_str.split(',')[1].split('.')[0]  # has format hhmmss
                hour = int(g_time_string[0:2])
                minute = int(g_time_string[2:4])
                second = int(g_time_string[4:6])
                day = int(line_str.split(',')[2])
                month = int(line_str.split(',')[3])
                year = int(line_str.split(',')[4])
                time_from_gps = datetime.datetime(year,month,day,hour,minute,second,tzinfo=None)
                cosmicdict['UTCUnixTime'] = (time_from_gps - datetime.datetime(1970, 1, 1)).total_seconds()
                cosmicdict['UTCUnixTime'] += 1
        if gps_type == "$GPGGA":
                # sanity check
                if (line_str.count(',') == 14):
                # use this as documentation for the string: http://aprs.gids.nl/nmea/#gga
                    lat = line_str.split(',')[2]
                    lat = float(lat[0:2])
                    minutes = line_str.split(',')[2]
                    minutes = float(minutes[2:len(minutes)])
                    lat += minutes / 60.
                    if line_str.split(',')[3] == 'S':
                        lat = -lat
                    lon = line_str.split(',')[4]
                    lon = float(lon[0:3])
                    minutes = line_str.split(',')[4]
                    minutes = float(minutes[3:len(minutes)])
                    lon += minutes / 60.
                    if line_str.split(',')[5] == 'W':
                        lon = -lon
                cosmicdict['Latitude'] = lat
                cosmicdict['Longitude'] = lon
                if (eventcount >= 0) :
                    geohash_pos="\""+geohash.encode(lat,lon)+"\""
                    data = []
                    data.append("{measurement},id={DeviceID} geohash={geohash_pos},event_count={event_count} {timestamp}"
                    .format(measurement='CosmicPiV1.8.1_freq',
                            DeviceID=cosmicdict['DeviceID'],
                            geohash_pos=geohash_pos,
                            event_count=eventcount,
                            timestamp=int(cosmicdict['UTCUnixTime'])))
                    print(data)
                    client.write_points(data, database='cosmicpilocal', time_precision='s', batch_size=1, protocol='line')
                    eventcount=0
                    if mqtt_ok==1:
                        ret = client1.publish("cosmicpi/worldmap",str(data))

        if data_type == "Event":
            if ((line_str.count(':') == 3) and (line_str.count(';') == 1)):
                sub_sec_string = line_str.split(':')[2]
                sub_sec_string = sub_sec_string.split(';')[0]
                if sub_sec_string.count('/') == 1:
                    # this is the newer format and we need to divide the first number by the second one
                    divisors = sub_sec_string.split('/')
                    current_subSeconds = float(divisors[0]) / float(divisors[1])
                cosmicdict['SubSeconds'] = current_subSeconds
            #print(cosmicdict)
            #conversion to ns for influx
            #add s and ns, then multiply by 1e9
            nstimestamp = cosmicdict['UTCUnixTime']+cosmicdict['SubSeconds']
            nstimestamp = nstimestamp*1e9
            nstimestamp = int(nstimestamp)
            eventcount = eventcount + 1
            data = []
            data.append("{measurement},id={DeviceID} lat={latitude},lon={longitude},Temp={Temp},Hum={Hum},Accelx={Accelx},Accely={Accely},Accelz={Accelz},Magx={Magx},Magy={Magy},Magz={Magz},Press={Pressx},Alt={Altx} {timestamp}"
            .format(measurement='CosmicPiV1.8.1',
                    DeviceID=cosmicdict['DeviceID'],
                    latitude=cosmicdict['Latitude'],
                    longitude=cosmicdict['Longitude'],
                    Temp=cosmicdict['TemperatureC'],
                    Hum=cosmicdict['Humidity'],
                    Accelx=cosmicdict['AccelX'],
                    Accely=cosmicdict['AccelY'],
                    Accelz=cosmicdict['AccelZ'],
                    Magx=cosmicdict['MagX'],
                    Magy=cosmicdict['MagY'],
                    Magz=cosmicdict['MagZ'],
                    Pressx=cosmicdict['Pressure'],
                    Altx=cosmicdict['Altitude'],
                    timestamp=nstimestamp))
            print(data)
            client.write_points(data, database='cosmicpilocal', time_precision='n', batch_size=1, protocol='line')
            if mqtt_ok==1:
                ret = client1.publish("cosmicpi/1.8.1",str(data))
