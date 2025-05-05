from flask import Blueprint, request, jsonify, render_template
from app.models import SensorData
from app import db


main_bp = Blueprint('main', __name__)

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
    latest_data = SensorData.query.order_by(SensorData.timestamp.desc()).first()
    if latest_data:
        return jsonify({
            'pitch': latest_data.pitch,
            'yaw': latest_data.yaw,
            'roll': latest_data.roll,
            'gpsx': latest_data.gpsx,
            'gpsy': latest_data.gpsy,
            'gpsz': latest_data.gpsz,
            'pressure': latest_data.pressure,
            'altitude': latest_data.altitude,
            'temp': latest_data.temp,
            'Vx': latest_data.Vx,
            'Vy': latest_data.Vy,
            'Vz': latest_data.Vz,
            'Ax': latest_data.Ax,
            'Ay': latest_data.Ay,
            'Az': latest_data.Az,
            'Gx': latest_data.Gx,
            'Gy': latest_data.Gy,
            'Gz': latest_data.Gz,
            'last_qr_reading': latest_data.last_qr_reading,
            'timestamp': latest_data.timestamp.isoformat()
        })
    return jsonify({"message": "No data available"}), 404