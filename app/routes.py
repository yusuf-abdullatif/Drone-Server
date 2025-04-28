from flask import Blueprint, request, jsonify, render_template
from app.models import SensorData
from app import db
from datetime import datetime

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    # Remove db.app.app_context() and use direct queries
    if not SensorData.query.first():
        mock_data = SensorData(
            pitch=45.0,
            yaw=90.0,
            roll=10.0
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
        roll=data.get('roll', 0.0)
    )
    db.session.add(new_data)
    db.session.commit()
    return jsonify({"message": "Data saved!"}), 201