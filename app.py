import os
from flask import Flask, request, jsonify, make_response, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import eventlet
import socketio
from services import services

flaskapp = Flask(__name__)
CORS(flaskapp)

sio = socketio.Server(cors_allowed_origins='*')
app = app = socketio.WSGIApp(sio, flaskapp)

flaskapp.config['UPLOAD_FOLDER'] = './data/'
flaskapp.secret_key = 'qwertyuiop'


@flaskapp.route('/upload/image', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        image_data = services.process_image(
            request, flaskapp.config['UPLOAD_FOLDER'])
        return jsonify({
            'data': str(image_data)
        })
    else:
        return jsonify({'message': 'Upload a file!'})


@flaskapp.route('/upload/video', methods=['GET', 'POST'])
def upload_video():
    if request.method == 'POST':
        f = request.files['file']
        f.save(os.path.join(
            flaskapp.config['UPLOAD_FOLDER'], "videos", secure_filename(f.filename)))

        return jsonify({'x': True})


@sio.event
def connect(sid, environ):
    print('CONN:')
    print('connect', sid)


@sio.on('message')
def my_message(sid, data):
    print('MESSAGE:')
    print('message', data)


@sio.on('stream')
def my_stream(sid, data):
    print('STREAM:')
    sio.emit('replay', data)


@sio.event
def disconnect(sid):
    print('disconnect', sid)


if __name__ == '__main__':
    print('Hello')
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)
