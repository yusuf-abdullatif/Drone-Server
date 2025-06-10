from flask import Blueprint, request, jsonify, render_template
from flask_socketio import emit
from app import db, socketio # Assuming 'app' is your Flask app instance and db/socketio are initialized there
from app.models import SensorData
import cv2
import base64
import threading
from datetime import datetime
from flask_cors import CORS # Import CORS

main_bp = Blueprint('main', __name__)

CORS(main_bp,
     resources={r"/api/*": { # Apply to all routes starting with /api/
         "origins": "*", # Allow all origins (you can restrict this to 'http://192.168.137.72' if needed)
         "methods": ["GET", "POST", "OPTIONS"], # Explicitly allow OPTIONS
         "allow_headers": ["Content-Type", "Authorization"], # Allow common headers, add others if your client sends them
         "supports_credentials": True # If you plan to use cookies/auth later
}})

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
# No specific CORS decorator needed here if applied to blueprint or using the resources config above
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


@main_bp.route('/api/qrdata', methods=['POST'])
def receive_qr_data():
    data = request.get_json()
    latest = SensorData.query.order_by(SensorData.timestamp.desc()).first()

    if latest:
        latest.last_qr_reading = data.get('last_qr_reading', '')
        db.session.commit()
        return jsonify({"message": "QR Data updated!"}), 200
    else:
        return jsonify({"error": "No data to update"}), 404

@main_bp.route('/api/latest')
# No specific CORS decorator needed here if applied to blueprint or using the resources config above
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

@main_bp.route('/api/video', methods=['POST', 'OPTIONS']) # Add 'OPTIONS'
# No specific CORS decorator needed here if applied to blueprint or using the resources config above
def receive_video():
    # Browsers will first send an OPTIONS request for POST with certain content types
    # Flask-CORS usually handles this automatically if configured at the app or blueprint level.
    # If you see issues with preflight, ensure OPTIONS is handled or Flask-CORS is set up correctly.
    if request.method == 'OPTIONS':
        # Flask-CORS handles this if set up on the blueprint or app
        # For manual handling (less common with Flask-CORS):
        # response = jsonify({"message": "CORS preflight OK"})
        # response.headers.add('Access-Control-Allow-Origin', '*')
        # response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        # response.headers.add('Access-Control-Allow-Methods', 'POST,GET,OPTIONS')
        # return response, 200
        pass # Flask-CORS will handle it.

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