


ActiveChannelType = 1
TemperatureChannelType = 2

sensorDataTable = "SensorData"

import mysql.connector




db = mysql.connector.connect(
    host="phil.host",
    user="raspberrypi",
    password="raspberrypi",
    database = "RaspberryPi"
)
cursor = db.cursor()
cursor.execute("SELECT ChannelID, ChannelType FROM Channels")
Channels = cursor.fetchall()

cursor.execute("SELECT SensorID, SensorType, ChannelID FROM Sensors")
Sensors = cursor.fetchall()

cursor.execute("SELECT SensorType, SensorDataName FROM SensorTypes")
SensorTypes = cursor.fetchall()

for x in Channels:
    print(x)
    print(x[0])
for x in Sensors:
    print(x)
for x in SensorTypes:
    print(x)
