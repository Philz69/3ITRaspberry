

ActiveChannelType = 1
TemperatureChannelType = 2

sensorDataTable = "SensorData"

import mysql.connector


class ActiveChannel():

    channelType = ActiveChannelType

    def __init__(self, channelID, voltageSensorID = 0, currentSensorID = 0):
        self.channelID = channelID
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

class DataBase():

    ActiveChannels = []
    
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

        self.cursor.execute("SELECT SensorID, SensorType, ChannelID FROM Sensors")
        Sensors = self.cursor.fetchall()

        self.cursor.execute("SELECT SensorType, SensorDataName FROM SensorTypes")
        SensorTypes = self.cursor.fetchall()

        for sensorType in SensorTypes:
            if sensorType[1] == "voltage":
                self.voltageSensorType = sensorType[0]
            elif sensorType[1] == "current":
                self.currentSensorType = sensorType[0]


        for channel in Channels:
            if channel[1] == ActiveChannelType:
                self.ActiveChannels.append(ActiveChannel(channel[0]))

        for sensor in Sensors:
            for channel in self.ActiveChannels:
                if channel.channelID == sensor[2]:
                    if sensor[1] == self.voltageSensorType:
                        channel.voltageSensorID = sensor[0]
                    elif sensor[1] == self.currentSensorType:
                        channel.currentSensorID = sensor[0]

        for channel in self.ActiveChannels:
            channel.printIDs()

    def sendUpate(self, arduino):
        for i, channel in enumerate(arduino.ActiveChannels):
            self.ActiveChannels[i].sendUpdate(self.cursor, arduino.lastUpdate, channel.voltage, channel.current)
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