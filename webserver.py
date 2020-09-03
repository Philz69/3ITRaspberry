from flask import Flask, jsonify, render_template, request
from arduino import *
from database import *
from datetime import datetime
from datetime import timezone
from datetime import timedelta
import threading

arduino = Arduino()

database = DataBase()

app = Flask(__name__)

maxUpdateTime = 1000
maxUpdateTimedelta = timedelta(milliseconds=maxUpdateTime)
lastUpdate = datetime.now(timezone.utc)

@app.route('/_get_channels')
def get_channels():
    return jsonify(arduino.lastReponse)

@app.route('/_send_command', methods = ['POST'])
def send_command():
   json = request.get_json()
   if(json['command'] == "startmppt"):
      channelNumber = int(json['channelNumber'])
      arduino.ActiveChannels[channelNumber].StartMPPT()
      response = {'mode': arduino.ActiveChannels[channelNumber].mode, 'channelNumber': channelNumber}
      return jsonify(response)
   if(json['command'] == "stopmppt"):
      channelNumber = int(json['channelNumber'])
      arduino.ActiveChannels[channelNumber].StopMPPT()
      response = {'mode': arduino.ActiveChannels[channelNumber].mode, 'channelNumber': channelNumber}
      return jsonify(response)
   elif(json['command'] == "sweep"):
      channelNumber = int(json['channelNumber'])
      arduino.ActiveChannels[channelNumber].Sweep()
      response = {'mode': arduino.ActiveChannels[channelNumber].mode, 'channelNumber': channelNumber}
      return jsonify(response)
@app.route("/")
def hello():
   now = datetime.now()
   timeString = now.strftime("%Y-%m-%d %H:%M")
   templateData = {
      'title' : 'HELLO!',
      'time': timeString,
     'arduino': arduino
      }
   return render_template('index.html', **templateData)
if __name__ == "__main__":
   arduino.waitForReady()
   arduino.Update()
   flaskThread = threading.Thread(target=app.run, args=('0.0.0.0', 8080, False))
   flaskThread.daemon=True
   flaskThread.start()
   while(True):
      arduino.processResponse()
      if(datetime.now(timezone.utc) - lastUpdate > maxUpdateTimedelta):
      #    start = datetime.now(timezone.utc)
         arduino.Update()
         database.sendUpate(arduino)
         #database.sendVoltage(arduino.lastUpdate, arduino.ActiveChannels[0].voltage) 
         #database.sendCurrent(arduino.lastUpdate, arduino.ActiveChannels[0].current) 
         #arduino.PrintStatus()
         lastUpdate = datetime.now(timezone.utc)
      #manualCommand()