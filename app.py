
import sqlite3
from flask import Flask, g, render_template
from flask_socketio import SocketIO
import requests
import logging
import traceback
from contextlib import closing
import json
import threading


app = Flask(__name__,static_folder='static',static_url_path='')
app.config['SECRET_KEY'] = '***REMOVED***'
socketio = SocketIO(app)


api_url = r"***REMOVED***"
db_location = r"db/spot.db"

from datetime import datetime
from threading import Timer

class PeriodicTask(object):
    def __init__(self, interval, callback, daemon=True, **kwargs):
        self.interval = interval
        self.callback = callback
        self.daemon   = daemon
        self.kwargs   = kwargs

    def run(self):
        self.callback(**self.kwargs)
        t = Timer(self.interval, self.run)
        t.daemon = self.daemon
        t.start()


def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))

def init_db():
    create_command = "CREATE TABLE IF NOT EXISTS gps_points ( id INTEGER PRIMARY KEY NOT NULL, spot_id INTEGER, unix_time INTEGER, latitude DOUBLE, longitude DOUBLE, date_time NCHAR(24) )"
    db = get_db()
    with closing(db.cursor()) as cursor:
        cursor = cursor.execute(create_command)
    db.commit()

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(db_location)
        db.row_factory = make_dicts
    return db 

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.before_first_request
def setup():
    init_db()
    parse_spot_data()
    task = PeriodicTask(interval=1, callback=dummy_data)
    task.run()

def parse_spot_data():
    r = requests.get(api_url)
    if r.status_code == 200:
        response_data = r.json()['response']['feedMessageResponse']['messages']['message']
        upload_new_points(response_data)

def dummy_data():
    print "In here"
    socketio.emit('new points',{'data':'stuff'})

def upload_new_points(in_data):
    command = "INSERT INTO gps_points (spot_id, unix_time, latitude, longitude, date_time) VALUES ({spot_id},{unix_time},{latitude},{longitude},\"{date_time}\")"
    db = get_db()
    last_points = get_points()
    if len(last_points) > 0:
        last_data_time = last_points[len(last_points)-1]['unix_time']
    else:
        last_data_time = 0

    ordered_response_data = [r for r in sorted(in_data,key=lambda x: x['unixTime']) if (r['unixTime'] > last_data_time) and (r['messageType'].lower()=='track')]

    with closing(db.cursor()) as cursor:
        for p in ordered_response_data:
            cursor.execute(command.format(spot_id=p['id'],unix_time=p['unixTime'],latitude=p['latitude'],longitude=p['longitude'],date_time=p['dateTime']))
    db.commit()

    return ordered_response_data

def get_points():
    db = get_db()
    with closing(db.cursor()) as cursor:
        cursor.execute("SELECT * FROM gps_points ORDER BY unix_time")
        rv = cursor.fetchall() 
        return rv
    return []

@app.route('/')
def page():
    data = get_points()
    return render_template('index.html',data=json.dumps(data))

@socketio.on('my event')
def handle_my_custom_event(data):
    print('received args: ' + str(data))


if __name__ == "__main__":
    #app.run(host='0.0.0.0',debug=True)
    socketio.run(app,host='0.0.0.0',use_reloader=True)




