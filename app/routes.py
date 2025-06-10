from flask import Blueprint, request, jsonify, render_template
from flask_socketio import emit
# Assuming 'app' is your Flask app instance and db/socketio are initialized there
from app import db, socketio
from app.models import SensorData
import cv2
import base64
import threading
from datetime import datetime
from flask_cors import CORS # Import CORS

main_bp = Blueprint('main', __name__)

# Apply CORS to the blueprint
CORS(main_bp,
     resources={r"/api/*": { # Apply to all routes starting with /api/
         "origins": "*", # Allow all origins (you can restrict this to specific domains)
         "methods": ["GET", "POST", "OPTIONS"], # Explicitly allow OPTIONS for preflight requests
         "allow_headers": ["Content-Type", "Authorization"], # Allow common headers
         "supports_credentials": True # If you plan to use cookies/auth later
    }
})

latest_frame = None
frame_lock = threading.Lock()
# Global variable to store the arming status.
# In a real application, this would typically be stored in a database or a more persistent store.
system_armed_status = False

@main_bp.route('/')
def index():
    """
    Renders the main dashboard page.
    Initializes mock data if no sensor data exists in the database.
    """
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

    # Fetch all data (though only the latest is typically displayed on the frontend)
    # The frontend primarily uses the /api/latest endpoint, so this part is less critical for display.
    data = SensorData.query.order_by(SensorData.timestamp.desc()).all()
    return render_template('index.html', data=data)

@main_bp.route('/api/data', methods=['POST'])
def receive_data():
    """
    Receives sensor data from the client and saves it to the database.
    """
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
    """
    Receives QR code data and updates the latest sensor entry in the database.
    """
    data = request.get_json()
    latest = SensorData.query.order_by(SensorData.timestamp.desc()).first()

    if latest:
        latest.last_qr_reading = data.get('last_qr_reading', '')
        db.session.commit()
        return jsonify({"message": "QR Data updated!"}), 200
    else:
        return jsonify({"error": "No data to update"}), 404

@main_bp.route('/api/latest')
def get_latest_data():
    """
    Retrieves the latest sensor data and the current system arming status.
    """
    latest = SensorData.query.order_by(SensorData.timestamp.desc()).first()
    if not latest:
        # If no sensor data, return a default state including armed status
        return jsonify({
            "message": "No data available",
            "armed": system_armed_status,
            # Provide default values for other fields if no data
            "gpsx": 0.0, "gpsy": 0.0, "gpsz": 0.0,
            "pressure": 0.0, "altitude": 0.0, "temp": 0.0,
            "Vx": 0.0, "Vy": 0.0, "Vz": 0.0,
            "Ax": 0.0, "Ay": 0.0, "Az": 0.0,
            "Gx": 0.0, "Gy": 0.0, "Gz": 0.0,
            "pitch": 0.0, "yaw": 0.0, "roll": 0.0,
            "last_qr_reading": "",
            "timestamp": datetime.now().isoformat()
        }), 200 # Changed to 200 so frontend doesn't error out on 404

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
        "timestamp": latest.timestamp.isoformat(),
        "armed": system_armed_status # Include the armed status
    })

@main_bp.route('/api/arm', methods=['POST'])
def arm_system():
    """
    API endpoint to arm the system.
    Sets the global system_armed_status to True.
    """
    global system_armed_status
    system_armed_status = True
    # You might add logic here to trigger physical arming mechanisms
    print("System Armed!") # For debugging/logging
    return jsonify({"message": "System armed successfully!", "armed": True}), 200

@main_bp.route('/api/disarm', methods=['POST'])
def disarm_system():
    """
    API endpoint to disarm the system.
    Sets the global system_armed_status to False.
    """
    global system_armed_status
    system_armed_status = False
    # You might add logic here to trigger physical disarming mechanisms
    print("System Disarmed!") # For debugging/logging
    return jsonify({"message": "System disarmed successfully!", "armed": False}), 200


@main_bp.route('/api/video', methods=['POST', 'OPTIONS'])
def receive_video():
    """
    Receives video frames as binary data.
    Stores the latest frame in base64 format for broadcasting via Socket.IO.
    """
    if request.method == 'OPTIONS':
        # Flask-CORS handles preflight requests automatically if configured.
        # This block is primarily for understanding, not typically needed if CORS is set up correctly.
        pass

    global latest_frame
    frame_data = request.data
    with frame_lock:
        latest_frame = base64.b64encode(frame_data).decode('utf-8')
    return jsonify({"message": "Frame received"}), 200

def broadcast_frames():
    """
    Continuously broadcasts the latest video frame to connected Socket.IO clients.
    Runs in a separate thread.
    """
    global latest_frame
    while True:
        with frame_lock:
            if latest_frame:
                socketio.emit('video_frame', {'image': latest_frame})
        socketio.sleep(0.033)  # Adjust for desired FPS (e.g., 0.033 for ~30 FPS)

@socketio.on('connect')
def handle_connect():
    """
    Handles new Socket.IO client connections.
    Starts the video frame broadcasting thread if it's not already running.
    """
    if not hasattr(socketio, 'broadcast_thread') or not socketio.broadcast_thread.is_alive():
        socketio.broadcast_thread = threading.Thread(target=broadcast_frames)
        socketio.broadcast_thread.daemon = True # Allow the thread to exit when the main program exits
        socketio.broadcast_thread.start()
