from app import db
from datetime import datetime

class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    # Existing fields
    pitch = db.Column(db.Float)
    yaw = db.Column(db.Float)
    roll = db.Column(db.Float)

    # New fields
    gpsx = db.Column(db.Float)
    gpsy = db.Column(db.Float)
    gpsz = db.Column(db.Float)
    pressure = db.Column(db.Float)
    altitude = db.Column(db.Float)
    temp = db.Column(db.Float)
    Vx = db.Column(db.Float)
    Vy = db.Column(db.Float)
    Vz = db.Column(db.Float)
    Ax = db.Column(db.Float)
    Ay = db.Column(db.Float)
    Az = db.Column(db.Float)
    Gx = db.Column(db.Float)
    Gy = db.Column(db.Float)
    Gz = db.Column(db.Float)
    last_qr_reading = db.Column(db.String(200))