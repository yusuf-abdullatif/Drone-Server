# app/models.py
from app import db


class SensorData(db.Model):
    __tablename__ = 'sensor_data'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    pitch = db.Column(db.Float)
    yaw = db.Column(db.Float)
    roll = db.Column(db.Float)