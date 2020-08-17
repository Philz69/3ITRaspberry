from flask import Flask, jsonify, render_template, request
from arduino import *
from datetime import datetime
from datetime import timezone
from datetime import timedelta
import threading

arduino = Arduino()
app = Flask(__name__)

maxUpdateTime = 1000
maxUpdateTimedelta = timedelta(milliseconds=maxUpdateTime)

@app.route('/_get_channels')
def get_channels():
    return jsonify(arduino.lastReponse)

@app.route('/_send_command', methods = ['POST'])
def send_command():
   json = request.get_json()
   if(json.command == "mppt"):
      print("AYYY")
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
   flaskThread = threading.Thread(target=app.run(host='0.0.0.0', port=800, debug=False))
   flaskThread.daemon=True
   flaskThread.start()