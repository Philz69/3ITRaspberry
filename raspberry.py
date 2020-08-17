from arduino import *
from database import *
from datetime import datetime
from datetime import timezone
from datetime import timedelta

start = datetime.now(timezone.utc)





arduino = Arduino()

maxUpdateTime = 1000
maxUpdateTimedelta = timedelta(milliseconds=maxUpdateTime)

print(datetime.now(timezone.utc))
arduino.waitForReady()
print("Arduino is ready")

#arduino.Update()
#arduino.PrintStatus()
#
#arduino.SweepActiveChannels()
#arduino.getSweepResult()
#arduino.PrintStatus()
#
lastUpdate = datetime.now(timezone.utc)
#arduino.Update()
#arduino.PrintStatus()

arduino.StartMPPTActiveChannels()


database = DataBase()



while(True):
    if(datetime.now(timezone.utc) - lastUpdate > maxUpdateTimedelta):
    #    start = datetime.now(timezone.utc)
        arduino.Update()
        database.sendUpate(arduino)
        #database.sendVoltage(arduino.lastUpdate, arduino.ActiveChannels[0].voltage) 
        #database.sendCurrent(arduino.lastUpdate, arduino.ActiveChannels[0].current) 
        arduino.PrintStatus()
        lastUpdate = datetime.now(timezone.utc)
    #manualCommand()
    #print(getResponse())

#print(datetime.now(timezone.utc) - start)
