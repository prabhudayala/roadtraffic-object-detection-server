import os
from flask import Flask, request, jsonify, make_response, send_file, Response
from flask_cors import CORS
from werkzeug.utils import secure_filename
import eventlet
# import socketio
from services import services

flaskapp = Flask(__name__)
CORS(flaskapp)

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


@flaskapp.route('/video_feed')
def video_feed():
    return Response(services.process_live(), mimetype="multipart/x-mixed-replace; boundary=frame")


@flaskapp.route('/stop_feed')
def stop_feed():
    services.stop_stream()
    return Response()


if __name__ == '__main__':
    print('Hello')
    flaskapp.run(host="0.0.0.0", port=5000, debug=True)
