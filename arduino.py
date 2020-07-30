from dataclasses import dataclass
import serial
import json

nmbPassiveChannels = 8
nmbActiveChannels = 8
nmbTemperatureChannels = 16

sweepingMode = "Sweeping"
MPPTMode = "MPPT"
idleMode = "Idle"

ser = serial.Serial('COM3', 115200, timeout=10)

@dataclass
class SweepResult:
    time: float = 0
    voltage = []
    current = []



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
        response = getResponse()
        response = json.loads(response)
        for channel in self.TemperatureChannels:
            channel.temperature = response['channels']['TemperatureChannels'][channel.channelNumber]['temperature']
        for channel in self.PassiveChannels:
            channel.voltage = response['channels']['PassiveChannels'][channel.channelNumber]['voltage']
            channel.current = response['channels']['PassiveChannels'][channel.channelNumber]['current']
        for channel in self.ActiveChannels:
            channel.voltage = response['channels']['ActiveChannels'][channel.channelNumber]['voltage']
            channel.current = response['channels']['ActiveChannels'][channel.channelNumber]['current']

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


    def PrintStatus(self):
        print("Arduino Channels:")
        print("Temperature:")
        for i in range(0, 16):
            print(str(i) + ": " + str(self.TemperatureChannels[i].temperature))
        print("ActiveChannels")
        for i in range(0, 8):
            print(str(i) + "|Voltage" ": " + str(self.ActiveChannels[i].voltage) +
            "|Current: " + str(self.ActiveChannels[i].current))
        print("PassiveChannels")
        for i in range(0, 8):
            print(str(i) + "|Voltage" ": " + str(self.PassiveChannels[i].voltage) + 
            "|Current: " + str(self.PassiveChannels[i].current))
        print(flush=True)