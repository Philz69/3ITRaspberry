from dataclasses import dataclass
import serial
import json
from datetime import datetime
from datetime import timezone
from datetime import timedelta

SQLTimeFormat ="%Y-%m-%d %H:%M:%S"

nmbPassiveChannels = 8
nmbActiveChannels = 9
nmbTemperatureChannels = 16

sweepingMode = 2
MPPTMode = 1
idleMode = 0

ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)

@dataclass
class SweepResult:
    startTime = datetime.now(timezone.utc)
    startTimeMS: float = 0
    endTimeMS: float = 0
    voltage = []
    current = []
    sent = False
    done = False 


def manualCommand():
    message = input('What to send?')
    ser.write(message.encode())


def sendCommand(command):
    command = command + '\n'
    print(command.encode())
    ser.write(command.encode())
    return 1


def getResponse():
    response = str(ser.readline())[2:-5]
    return response


class TemperatureChannel:
    def __init__(self, channelNumber):
        self.channelNumber = channelNumber
        self.temperature = 0


class PassiveChannel:
    def __init__(self, channelNumber):
        self.channelNumber = channelNumber
        self.voltage = 0
        self.current = 0


class ActiveChannel:


    def __init__(self, channelNumber):
        self.channelNumber = channelNumber
        self.voltage = 0
        self.current = 0
        self.mode = idleMode
        self.sweepResult = SweepResult()

    def Sweep(self):
        sendCommand("SweepActiveChannel_" + str(self.channelNumber))
        self.mode = sweepingMode

    def StartMPPT(self):
        sendCommand("StartMPPTActiveChannel_" + str(self.channelNumber))
        self.mode = MPPTMode

    def StopMPPT(self):
        sendCommand("StopMPPTActiveChannel_" + str(self.channelNumber))
        self.mode = idleMode

class Arduino():

    ActiveChannels = []
    TemperatureChannels = []
    PassiveChannels = []

    def __init__(self):
        for i in range(0, nmbPassiveChannels):
            self.PassiveChannels.append(PassiveChannel(i))
        for i in range(0, nmbActiveChannels):
            self.ActiveChannels.append(ActiveChannel(i))
        for i in range(0, nmbTemperatureChannels):
            self.TemperatureChannels.append(TemperatureChannel(i))

    def waitForReady(self):
        while(not "Ready" in str(ser.readline())):
            pass

    def Update(self):
        sendCommand("Update")
        self.processResponse()
        #self.lastReponse = response
        #self.lastUpdate = datetime.now(timezone.utc).strftime(SQLTimeFormat)
        #for channel in self.TemperatureChannels:
        #    channel.temperature = response['channels']['TemperatureChannels'][channel.channelNumber]['temperature']
        #for channel in self.PassiveChannels:
        #    channel.voltage = response['channels']['PassiveChannels'][channel.channelNumber]['voltage']
        #    channel.current = response['channels']['PassiveChannels'][channel.channelNumber]['current']
        #for channel in self.ActiveChannels:
        #    channel.voltage = response['channels']['ActiveChannels'][channel.channelNumber]['voltage']
        #    channel.current = response['channels']['ActiveChannels'][channel.channelNumber]['current']
        #    channel.mode = response['channels']['ActiveChannels'][channel.channelNumber]['mode']

    def SweepActiveChannels(self):
        for channel in  self.ActiveChannels:
            channel.sweepResult.voltage.clear()
            channel.sweepResult.current.clear()
            channel.Sweep()

    def StartMPPTActiveChannels(self):
        for channel in self.ActiveChannels:
            channel.StartMPPT()

    def getSweepResult(self):
       done = 0
       while(not done == 8):
            response = getResponse()
            print(response)
            try:
                response = json.loads(response)
                channelNumber = response["sweepResults"]["channel"]
                self.ActiveChannels[channelNumber].sweepResult.time = response["time"]
                for i,voltage in enumerate(response["sweepResults"]["voltage"]):
                    self.ActiveChannels[channelNumber].sweepResult.voltage.insert(i, voltage)
                for i,current in enumerate(response["sweepResults"]["current"]):
                    self.ActiveChannels[channelNumber].sweepResult.current.insert(i, current)
                if response["sweepResults"]["progress"] >= 244/255:
                    self.ActiveChannels[channelNumber].mode = idleMode 
                    done += 1
            except json.JSONDecodeError:
                print("JSON Error")

    def processResponse(self):
        try:
            response = getResponse()
            response = json.loads(response)
            self.lastReponse = response
            self.lastUpdate = datetime.now(timezone.utc).strftime(SQLTimeFormat)
            try:
                for channel in self.TemperatureChannels:
                    channel.temperature = response['channels']['TemperatureChannels'][channel.channelNumber]['temperature']
                for channel in self.PassiveChannels:
                    channel.voltage = response['channels']['PassiveChannels'][channel.channelNumber]['voltage']
                    channel.current = response['channels']['PassiveChannels'][channel.channelNumber]['current']
                for channel in self.ActiveChannels:
                    channel.voltage = response['channels']['ActiveChannels'][channel.channelNumber]['voltage']
                    channel.current = response['channels']['ActiveChannels'][channel.channelNumber]['current']
                    channel.mode = response['channels']['ActiveChannels'][channel.channelNumber]['mode']

            except KeyError:
                try:
                    channelNumber = response["sweepResults"]["channel"]
                    if response["sweepResults"]["progress"] <= 1/255:
                        self.ActiveChannels[channelNumber].sweepResult.startTime = datetime.now(timezone.utc)
                        self.ActiveChannels[channelNumber].sweepResult.startTimeMS = response["time"]
                        self.ActiveChannels[channelNumber].sweepResult.voltage.clear()
                        self.ActiveChannels[channelNumber].sweepResult.current.clear()
                        self.ActiveChannels[channelNumber].sweepResult.sent = False
                    for i,voltage in enumerate(response["sweepResults"]["voltage"]):
                        self.ActiveChannels[channelNumber].sweepResult.voltage.insert(i, voltage)
                    for i,current in enumerate(response["sweepResults"]["current"]):
                        self.ActiveChannels[channelNumber].sweepResult.current.insert(i, current)
                    if response["sweepResults"]["progress"] >= 244/255:
                        self.ActiveChannels[channelNumber].mode = idleMode 
                        self.ActiveChannels[channelNumber].sweepResult.endTimeMS = response["time"]
                        self.ActiveChannels[channelNumber].sweepResult.done = True
                    print(response)
                except json.JSONDecodeError:
                    print("JSON Error")
        except json.JSONDecodeError:
            print("JSON Error")

    def PrintStatus(self):
        print("Last Update Time:" + str(self.lastUpdate))
        print("Arduino Channels:")
        print("Temperature:")
        for channel in self.TemperatureChannels:
            print(str(channel.channelNumber) + ": " + str(channel.temperature))
        print("ActiveChannels")
        for channel in self.ActiveChannels:
            print(str(channel.channelNumber) + "|Voltage" ": " + str(channel.voltage) +
            "|Current: " + str(channel.current))
        print("PassiveChannels")
        for channel in self.PassiveChannels:
            print(str(channel.channelNumber) + "|Voltage" ": " + str(channel.voltage) + 
            "|Current: " + str(channel.current))
        print(flush=True)