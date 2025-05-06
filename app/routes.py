from flask import Blueprint, request, jsonify, render_template
from flask_socketio import emit
from app import db, socketio
from app.models import SensorData
import cv2
import base64
import threading
from datetime import datetime


main_bp = Blueprint('main', __name__)
latest_frame = None
frame_lock = threading.Lock()


@main_bp.route('/')
def index():
    if not SensorData.query.first():
        mock_data = SensorData(
            pitch=0.0, yaw=0.0, roll=0.0,
            gpsx=0.0, gpsy=0.0, gpsz=0.0,
            pressure=1013.25, altitude=0.0, temp=25.0,
            Vx=0.0, Vy=0.0, Vz=0.0,
            Ax=0.0, Ay=0.0, Az=0.0,
            Gx=0.0, Gy=0.0, Gz=0.0,
            last_qr_reading="Scan QR code..."
        )
        db.session.add(mock_data)
        db.session.commit()

    data = SensorData.query.order_by(SensorData.timestamp.desc()).all()
    return render_template('index.html', data=data)

@main_bp.route('/api/data', methods=['POST'])
def receive_data():
    data = request.get_json()
    new_data = SensorData(
        pitch=data.get('pitch', 0.0),
        yaw=data.get('yaw', 0.0),
        roll=data.get('roll', 0.0),
        gpsx=data.get('gpsx', 0.0),
        gpsy=data.get('gpsy', 0.0),
        gpsz=data.get('gpsz', 0.0),
        pressure=data.get('pressure', 0.0),
        altitude=data.get('altitude', 0.0),
        temp=data.get('temp', 0.0),
        Vx=data.get('Vx', 0.0),
        Vy=data.get('Vy', 0.0),
        Vz=data.get('Vz', 0.0),
        Ax=data.get('Ax', 0.0),
        Ay=data.get('Ay', 0.0),
        Az=data.get('Az', 0.0),
        Gx=data.get('Gx', 0.0),
        Gy=data.get('Gy', 0.0),
        Gz=data.get('Gz', 0.0),
        last_qr_reading=data.get('last_qr_reading', '')
    )
    db.session.add(new_data)
    db.session.commit()
    return jsonify({"message": "Data saved!"}), 201


@main_bp.route('/api/latest')
def get_latest_data():
    latest = SensorData.query.order_by(SensorData.timestamp.desc()).first()
    if not latest:
        return jsonify({"message": "No data available"}), 404

    return jsonify({
        "gpsx": latest.gpsx,
        "gpsy": latest.gpsy,
        "gpsz": latest.gpsz,
        "pressure": latest.pressure,
        "altitude": latest.altitude,
        "temp": latest.temp,
        "Vx": latest.Vx,
        "Vy": latest.Vy,
        "Vz": latest.Vz,
        "Ax": latest.Ax,
        "Ay": latest.Ay,
        "Az": latest.Az,
        "Gx": latest.Gx,
        "Gy": latest.Gy,
        "Gz": latest.Gz,
        "pitch": latest.pitch,
        "yaw": latest.yaw,
        "roll": latest.roll,
        "last_qr_reading": latest.last_qr_reading,
        "timestamp": latest.timestamp.isoformat()
    })

@main_bp.route('/api/video', methods=['POST'])
def receive_video():
    global latest_frame
    frame_data = request.data
    with frame_lock:
        latest_frame = base64.b64encode(frame_data).decode('utf-8')
    return jsonify({"message": "Frame received"}), 200

def broadcast_frames():
    global latest_frame
    while True:
        with frame_lock:
            if latest_frame:
                socketio.emit('video_frame', {'image': latest_frame})
        socketio.sleep(0.033)  # ~30 FPS

@socketio.on('connect')
def handle_connect():
    if not hasattr(socketio, 'broadcast_thread') or not socketio.broadcast_thread.is_alive():
        socketio.broadcast_thread = threading.Thread(target=broadcast_frames)
        socketio.broadcast_thread.daemon = True
        socketio.broadcast_thread.start()