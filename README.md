# grafana_dashboards
Cosmic Pi V1.8.1 software: Grafana Visualisations.
NB we're using InfluxDB under the hood and Grafana V6, since it's compatible with the Pi Zero W (ARM v6).
The database look like this:
Database: cosmicpilocal
Measurements: 

  measurement 1 ='CosmicPiV1.8.1_freq', seconds timebase
  
    DeviceID=MAC address in integer format,
    
    geohash_pos= The geohash of the device position, generated from the geohash python library
    
    event_count= Cumulative events in the last full second,
    
    timestamp= Unix timestamp (seconds) for the time the data was entered)
    
  measurement 2 ='CosmicPiV1.8.1', nanoseconds timebase
  
    DeviceID=MAC address in integer format,
    
    latitude=Longitude, decimal format
    
    longitude=Latitude, decimal format
    
    Temp=Temperature in Celcius
    
    Hum=Relative Humidity in %
    
    Accelx=Acceleration, X axis in m/s/s
    
    Accely=Acceleration, Y axis in m/s/s
    
    Accelz=Acceleration, Z axis in m/s/s
    
    Magx= Magnetic Field, X axis in mT
    
    Magy= Magnetic Field, Y axis in mT
    
    Magz= Magnetic Field, Z axis in mT
    
    Pressx= Pressure in mb
    
    Altx= Altitude in meters
    
    timestamp=nstimestamp of event
    
Why are there two measurements?

One (CosmicPiV1.8.1_freq) is created every second, the other is created for every event (indexed by nanosecond). Because of this it was easiest to store the information in two different measurements. When we want individual, highly precise data we can look at CosmicPiV1.8.1, and when we want to see agregated rates or detection locations, we can use CosmicPiV1.8.1_freq.

With this information you can write your own queries and create new visualisations.

Note that unless your unit is connected to the internet, you won't be able to do the world map visualisation (it requires cached data from Open Street Map). 

If you have an internet connection for your Cosmic Pi, the data is also sent via MQTT to a central server, where one day we'll have a global dashboard. The MQTT server is cosmicpidata.mooo.com, port 1833. A username and password are required, just to prevent unwanted guests. You can find the details in the cosmicpi-detector.py script. 

If you have an old Cosmic Pi (V. 1.5 or greater) you should be able to upgrade to this new dashboard. 

By default the unit presents the main dashboard on access to 192.168.0.1 (or the locally assigned IP address or http://cosmicpi if you have it connected to the internet). If you want to login and change/customise your dashboard, you can do it with the admin account, the default password is "MuonsFROMSp8ce" (enter it without quotations!).
    
PS there is no default retention policy on the influxdb, your SD card will fill up eventually (>years!) if you leave it on forever, probably. 

PPS The number of records you can retrive has been limited on the Raspberry Pi Zero, since it's only a little computer. To prevent crashing, it's suggested that you don't retrive more than 24h worth of data in one query (i.e. LIMIT 86400). This is within the maximum value and shouldn't use up too much memory on the Raspberry. 
