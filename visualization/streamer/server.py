from flask import Flask, render_template
from flask.ext.socketio import SocketIO
import json
import oauth2 as oauth
import urllib2 as urllib
import sys
import re



app = Flask(__name__)
socketio = SocketIO(app)

@app.route("/realtime")
def index():
	return render_template('index.html',)

@app.route("/map")
def map():
	return render_template('map.html',)

@app.route("/bound")
def bound():
	return render_template('bound.html',)



if __name__ == "__main__":
	socketio.run(app)