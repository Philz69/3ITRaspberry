import mysql.connector
from arduino import *
from datetime import datetime
from datetime import timezone
from datetime import timedelta

start = datetime.now(timezone.utc)


mydb = mysql.connector.connect(
    host="phil.host",
    user="raspberrypi",
    password="raspberrypi"
)

print(mydb)

mydb

arduino = Arduino()

maxUpdateTime = 1000
maxUpdateTimedelta = timedelta(milliseconds=maxUpdateTime)

print(datetime.now(timezone.utc))
arduino.waitForReady()
print("Arduino is ready")


lastUpdate = datetime.now(timezone.utc)
while(True):
    arduino.SweepActiveChannels()
    arduino.getSweepResult()

    #if(datetime.now(timezone.utc) - lastUpdate > maxUpdateTimedelta):
    #    start = datetime.now(timezone.utc)
    #    arduino.Update()
    #    arduino.PrintStatus()
    #manualCommand()
    #print(getResponse())

print(datetime.now(timezone.utc) - start)
