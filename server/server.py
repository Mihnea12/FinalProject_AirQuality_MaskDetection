from crypt import methods
from PIL import Image
from flask import Flask, render_template, request, redirect
import json
from datetime import datetime
import html
import os
from flask_mqtt import Mqtt
import eventlet
from flask_socketio import SocketIO
from flask_bootstrap import Bootstrap
from flask_mongoengine import MongoEngine, MongoEngineSessionInterface
from flask_pymongo import pymongo
import db
from flask_bootstrap import Bootstrap
from flask_datepicker import datepicker



CO2 = 0
AQI = 0
img_mask = 0
FAN = False
PERS = 0
ppm_values = []
time_values = []
aqi_values = []

wireless_ppm_values = []
wireless_aqi_values = []
wireless_time_values = []

#eventlet.monkey_patch()

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['MQTT_BROKER_URL'] = 'broker.emqx.io'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = 'emqx'
app.config['MQTT_PASSWORD'] = 'public'
app.config['MQTT_REFRESH_TIME'] = 1.0  # refresh time in seconds

mqtt = Mqtt(app)

socketio = SocketIO(app)
bootstrap = Bootstrap(app)
datepicker(app)

UPLOAD_FOLDER ='static/files'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe('mihnea/ppm')
    mqtt.subscribe('mihnea/aqi')
    mqtt.subscribe('mihnea/time')


@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )
    print(data)
    if data["topic"] == 'mihnea/ppm':
        if len(wireless_ppm_values) > 9:
            wireless_ppm_values.pop(0)
        wireless_ppm_values.append(data["payload"])
    if data["topic"] == 'mihnea/aqi':
        if len(wireless_aqi_values) > 9:
            wireless_aqi_values.pop(0)
        wireless_aqi_values.append(data["payload"])
    if data["topic"] == 'mihnea/time':
        if len(wireless_time_values) > 9:
            wireless_time_values.pop(0)
        wireless_time_values.append(data["payload"])
    
    print(wireless_ppm_values)
    print(wireless_aqi_values)
    print(wireless_time_values)

@app.route("/")
def home():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    if len(ppm_values) > 9:
        ppm_values.pop(0)
        time_values.pop(0)
        aqi_values.pop(0)
    ppm_values.append(int(CO2))
    aqi_values.append(int(AQI))
    time_values.append(current_time)

    return render_template('home.html', ppm_co2 = CO2, aqi = AQI, mask = img_mask, fan = FAN, pers = PERS, ppm_json = ppm_values, time_json = time_values, aqi_json = aqi_values, w_ppm_json = wireless_ppm_values, w_aqi_json = wireless_aqi_values, w_time_json = wireless_time_values)

@app.route("/data", methods=['POST'])
def getData():
    value_co2 = request.form['co2']
    value_aqi = request.form['aqi']
    value_fan = request.form['fan']
    print(value_fan)
    global CO2 
    global AQI
    global FAN
    FAN = value_fan
    CO2 = value_co2 
    AQI = value_aqi

    return redirect("/")

@app.route("/mask", methods=['POST'])
def getMask():

    file = request.files['img']
    pers = request.form['pers']
    global PERS
    PERS = pers
    # Read the image via file.stream
    path = './static/savedimage.jpeg'
    file.save(path)
    global img_mask
    img_mask = path
    return redirect("/")

@app.route("/file", methods=['POST'])
def loudFile():
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
        uploaded_file.save(file_path)
    return redirect("/")

@app.route("/istoric")
def istoric():
    #test = 
    for data in db.collection.find():
        print(data['aqi'])

    return render_template('istoric.html')

if __name__ == '__main__':
    # important: Do not use reloader because this will create two Flask instances.
    # Flask-MQTT only supports running with one instance
    #socketio.run(app, host='0.0.0.0', port=5000, use_reloader=False, debug=False)
    app.run(port=5000)
    
    

