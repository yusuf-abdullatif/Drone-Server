from flask import Blueprint, request, jsonify, render_template, Response
from flask_socketio import emit
from app import db, socketio
from app.models import SensorData
import cv2
import base64
import threading
from datetime import datetime
from flask_cors import CORS
import time
import re  # Import regex for parsing multipart boundaries

main_bp = Blueprint('main', __name__)

# Apply CORS to the blueprint
CORS(main_bp,
     resources={r"/api/*": {
         "origins": "*",
         "methods": ["GET", "POST", "OPTIONS"],
         "allow_headers": ["Content-Type", "Authorization"],
         "supports_credentials": True
     }
     })

latest_frame = None
frame_lock = threading.Lock()
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
        return jsonify({
            "message": "No data available",
            "armed": system_armed_status,
            "gpsx": 0.0, "gpsy": 0.0, "gpsz": 0.0,
            "pressure": 0.0, "altitude": 0.0, "temp": 0.0,
            "Vx": 0.0, "Vy": 0.0, "Vz": 0.0,
            "Ax": 0.0, "Ay": 0.0, "Az": 0.0,
            "Gx": 0.0, "Gy": 0.0, "Gz": 0.0,
            "pitch": 0.0, "yaw": 0.0, "roll": 0.0,
            "last_qr_reading": "",
            "timestamp": datetime.now().isoformat()
        }), 200

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
        "armed": system_armed_status
    })


@main_bp.route('/api/arm', methods=['POST'])
def arm_system():
    """
    API endpoint to arm the system.
    Sets the global system_armed_status to True.
    """
    global system_armed_status
    system_armed_status = True
    print("System Armed!")
    return jsonify({"message": "System armed successfully!", "armed": True}), 200


@main_bp.route('/api/disarm', methods=['POST'])
def disarm_system():
    """
    API endpoint to disarm the system.
    Sets the global system_armed_status to False.
    """
    global system_armed_status
    system_armed_status = False
    print("System Disarmed!")
    return jsonify({"message": "System disarmed successfully!", "armed": False}), 200


@main_bp.route('/api/video', methods=['POST'])
def receive_video():
    """
    Receives video frames as a continuous multipart/x-mixed-replace stream.
    Parses individual JPEG frames and stores the latest one.
    """
    global latest_frame

    # Get the boundary from the Content-Type header
    content_type = request.headers.get('Content-Type')
    if not content_type or 'boundary=' not in content_type:
        return jsonify({"error": "Missing or invalid Content-Type header with boundary"}), 400

    boundary = content_type.split('boundary=')[1].strip()

    # Define the delimiter that separates frames
    delimiter = f'--{boundary}'.encode('utf-8')

    # Read the raw request body stream
    stream = request.input_stream

    # Read until the first delimiter (preamble)
    buffer = b''
    while True:
        chunk = stream.read(4096)  # Read in chunks
        if not chunk:
            break  # Client disconnected
        buffer += chunk
        if delimiter in buffer:
            buffer = buffer.split(delimiter, 1)[1]  # Keep content after first delimiter
            break

    # Now, continuously read and parse frames
    while True:
        try:
            chunk = stream.read(4096)
            if not chunk:
                # Client disconnected or stream ended
                print("Client disconnected from /api/video or stream ended.")
                break

            buffer += chunk

            # Find the next delimiter
            next_delimiter_index = buffer.find(delimiter)

            if next_delimiter_index != -1:
                # Extract the part before the next delimiter (which contains header and frame data)
                part = buffer[:next_delimiter_index]
                buffer = buffer[next_delimiter_index + len(delimiter):]  # Keep content after delimiter

                # Split part into headers and body
                header_end = part.find(b'\r\n\r\n')
                if header_end != -1:
                    # headers = part[:header_end].decode('utf-8', errors='ignore')
                    frame_data = part[header_end + 4:].strip()  # +4 for \r\n\r\n

                    if frame_data:
                        with frame_lock:
                            latest_frame = frame_data
                        # Optional: Emit via Socket.IO if you want other clients to get immediate updates
                        # try:
                        #     # Assuming frame_data is JPEG, base64 encode for Socket.IO if needed
                        #     socketio.emit('video_frame', {'image': base64.b64encode(frame_data).decode('utf-8')})
                        # except Exception as e:
                        #     print(f"Error emitting video frame via Socket.IO: {e}")

        except Exception as e:
            print(f"Error processing video stream: {e}")
            break  # Exit loop on error

    return jsonify({"message": "Video stream reception ended"}), 200  # This response is sent when the stream ends


def generate_frames():
    """
    Generator function to stream video frames for the /video_feed route.
    """
    while True:
        with frame_lock:
            if latest_frame is None:
                # Send a small transparent GIF as a placeholder if no frame is available
                # This prevents the browser from showing a broken image icon.
                # A 1x1 transparent GIF (base64 encoded)
                placeholder_gif = b'R0lGODlhAQABAIAAAP///wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw=='
                yield (b'--frame\r\n'
                       b'Content-Type: image/gif\r\n'
                       b'Content-Length: ' + str(len(placeholder_gif)).encode('utf-8') + b'\r\n\r\n' +
                       base64.b64decode(placeholder_gif) + b'\r\n')
                time.sleep(0.1)  # Wait a bit before checking again
                continue

            frame = latest_frame  # Use a copy of the frame

        # Yield the frame in the multipart format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        time.sleep(0.033)  # Adjust for desired FPS (approx 30 FPS)


@main_bp.route('/video_feed')
def video_feed():
    """
    Video streaming route for the dashboard.
    """
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@socketio.on('connect')
def handle_connect():
    """
    Handles new Socket.IO client connections.
    """
    print("Client connected")
