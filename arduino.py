import serial
import json

nmbPassiveChannels = 8
nmbActiveChannels = 8
nmbTemperatureChannels = 16

ser = serial.Serial('COM3', 115200, timeout=10)


def manualCommand():
    message = input('What to send?')
    ser.write(message.encode())


def sendCommand(command):
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

    def Sweep(self):
        sendCommand("SweepActiveChannel_" + self.channelNumber)
        return getResponse()

    def StartMPPT(self):
        sendcommand("StartMPPTActiveChannel_" + self.channelNumber)

    def StopMPPT(self):
        sendcommand("StopMPPTActiveChannel_" + self.channelNumber)


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
        print(response['channels'])
        print(response['channels']['ActiveChannels'][1]['voltage'])
        for channel in self.TemperatureChannels:
            channel.temperature = response['channels']['TemperatureChannels'][channel.channelNumber]['temperature']
        for channel in self.PassiveChannels:
            channel.voltage = response['channels']['PassiveChannels'][channel.channelNumber]['voltage']
            channel.current = response['channels']['PassiveChannels'][channel.channelNumber]['current']
        for channel in self.ActiveChannels:
            channel.voltage = response['channels']['ActiveChannels'][channel.channelNumber]['voltage']
            channel.current = response['channels']['ActiveChannels'][channel.channelNumber]['current']

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