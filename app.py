from predict import Predictor
import flask
from flask import Flask
app = Flask(__name__, static_folder='.', static_url_path='/')

t = Predictor()

@app.route('/data')
def data():
    return flask.jsonify(t.final_data)

@app.route('/website')
def predict():
    hostname = flask.request.args.get("hostname")
    return flask.jsonify(t.predict(hostname))

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/style.css')
def style():
    return app.send_static_file('style.css')

@app.route('/d3.v4.min.js')
def d3():
    return app.send_static_file('d3.v4.min.js')