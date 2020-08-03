import itertools

ActiveChannelType = 1
TemperatureChannelType = 2

sensorDataTable = "SensorData"

import mysql.connector

class PassiveChannel():

    def __init__(self, channelID, channelType, voltageSensorID = 0, currentSensorID = 0):
        self.channelID = channelID
        self.channelType = channelType
        self.voltageSensorID = voltageSensorID
        self.currentSensorID = currentSensorID
    
    def sendUpdate(self, cursor, time, voltage, current):
        sql = "INSERT INTO " + sensorDataTable + "(time, SensorID, Data) VALUES (%s, %s, %s)"
        voltageVal = (time, self.voltageSensorID, voltage)
        currentVal = (time, self.currentSensorID, current)
        cursor.execute(sql,voltageVal)
        cursor.execute(sql,currentVal)

    def printIDs(self):
        print("channelID: " + str(self.channelID) + "| voltageID: " + str(self.voltageSensorID) + "| currentID: " + str(self.currentSensorID))



class TemperatureChannel():

    def __init__(self, channelID, channelType, sensorID = 0):
        self.channelID = channelID
        self.channelType = channelType
        self.sensorID = sensorID

    def sendUpdate(self, cursor, time, temperature):
        sql = "INSERT INTO " + sensorDataTable + "(time, SensorID, Data) VALUES (%s, %s, %s)"
        val = (time, self.sensorID, temperature)
        cursor.execute(sql,val)

    def printIDs(self):
        print("channelID: " + str(self.channelID) + "| sensorID: " + str(self.sensorID))

class ActiveChannel(PassiveChannel):
    pass

class DataBase():

    ActiveChannels = []
    TemperatureChannels = []
    PassiveChannels = []
    
    def __init__(self):
        self.db = mysql.connector.connect(
            host="phil.host",
            user="raspberrypi",
            password="raspberrypi",
            database = "RaspberryPi"
        )
        self.cursor = self.db.cursor()
        self.cursor.execute("SELECT ChannelID, ChannelType FROM Channels")
        Channels = self.cursor.fetchall()

        self.cursor.execute("SELECT ChannelType, Name FROM ChannelTypes")
        ChannelTypes = self.cursor.fetchall()

        self.cursor.execute("SELECT SensorID, SensorType, ChannelID FROM Sensors")
        Sensors = self.cursor.fetchall()

        self.cursor.execute("SELECT SensorType, SensorDataName FROM SensorTypes")
        SensorTypes = self.cursor.fetchall()

        for channelType in ChannelTypes:
            if channelType[1] == "ActiveChannel":
                self.ActiveChannelType = channelType[0]
            elif channelType[1] == "TemperatureChannel":
                self.TemperatureChannelType = channelType[0]
            elif channelType[1] == "PassiveChannel":
                self.PassiveChannelType = channelType[0]

        for sensorType in SensorTypes:
            if sensorType[1] == "voltage":
                self.voltageSensorType = sensorType[0]
            elif sensorType[1] == "current":
                self.currentSensorType = sensorType[0]
            elif sensorType[1] == "temperature":
                self.temperatureSensorType = sensorType[0]

        for channel in Channels:
            if channel[1] == self.ActiveChannelType:
                self.ActiveChannels.append(ActiveChannel(channel[0], self.ActiveChannelType))
            if channel[1] == self.TemperatureChannelType:
                self.TemperatureChannels.append(TemperatureChannel(channel[0], self.TemperatureChannelType))
            if channel[1] == self.PassiveChannelType:
                self.PassiveChannels.append(PassiveChannel(channel[0], self.PassiveChannelType))

        for sensor in Sensors:
            for passiveChannel in self.PassiveChannels:
                if passiveChannel.channelID == sensor[2]:
                    if sensor[1] == self.voltageSensorType:
                        passiveChannel.voltageSensorID = sensor[0]
                    elif sensor[1] == self.currentSensorType:
                        passiveChannel.currentSensorID = sensor[0]
                    break
            for activeChannel in self.ActiveChannels:
                if activeChannel.channelID == sensor[2]:
                    if sensor[1] == self.voltageSensorType:
                        activeChannel.voltageSensorID = sensor[0]
                    elif sensor[1] == self.currentSensorType:
                        activeChannel.currentSensorID = sensor[0]
                    break
            for temperatureChannel in self.TemperatureChannels:
                if temperatureChannel.channelID == sensor[2]:
                    if sensor[1] == self.temperatureSensorType:
                        temperatureChannel.sensorID = sensor[0]
                    break

        for channel in self.ActiveChannels:
            channel.printIDs()

    def sendUpate(self, arduino):
        for i, channel in enumerate(arduino.ActiveChannels):
            self.ActiveChannels[i].sendUpdate(self.cursor, arduino.lastUpdate, channel.voltage, channel.current)
            self.db.commit()
        for i, channel in enumerate(arduino.TemperatureChannels):
            self.TemperatureChannels[i].sendUpdate(self.cursor, arduino.lastUpdate, channel.temperature)
            self.db.commit()

    def sendVoltage(self, time, voltage):
        sensorID = 1
        sql = "INSERT INTO " + sensorDataTable + "(time, SensorID, Data) VALUES (%s, %s, %s)"
        val = (time, sensorID, voltage)
        self.cursor.execute(sql, val) 
        self.db.commit()

    def sendCurrent(self, time, current):
        sensorID = 2
        sql = "INSERT INTO " + sensorDataTable + "(time, SensorID, Data) VALUES (%s, %s, %s)"
        val = (time, sensorID, current)
        self.cursor.execute(sql, val) 
        self.db.commit()