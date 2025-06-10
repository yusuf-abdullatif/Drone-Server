import requests
import random
import time
import sys
from datetime import datetime


def generate_random_sensor_data():
    return {
        "pitch": random.uniform(0, 360),
        "yaw": random.uniform(0, 360),
        "roll": random.uniform(0, 360),
        "gpsx": random.uniform(-180, 180),
        "gpsy": random.uniform(-90, 90),
        "gpsz": random.uniform(0, 10000),
        "pressure": random.uniform(800, 1200),
        "altitude": random.uniform(-100, 5000),
        "temp": random.uniform(-20, 50),
        "Vx": random.uniform(-10, 10),
        "Vy": random.uniform(-10, 10),
        "Vz": random.uniform(-10, 10),
        "Ax": random.uniform(-20, 20),
        "Ay": random.uniform(-20, 20),
        "Az": random.uniform(-20, 20),
        "Gx": random.uniform(-3.14, 3.14),
        "Gy": random.uniform(-3.14, 3.14),
        "Gz": random.uniform(-3.14, 3.14)
    }


def generate_qr_data():
    return {
        "last_qr_reading": f"QR_{datetime.now().strftime('%H%M%S%f')}"
    }


def spam_data(target_url, interval=1):
    while True:
        try:
            # Send sensor data
            sensor_data = generate_random_sensor_data()
            sensor_response = requests.post(
                f"{target_url}/api/data",
                json=sensor_data,
                timeout=2
            )
            print(f"Sensor: {sensor_response.status_code}, {sensor_response.text}")

            # Send QR data
            qr_data = generate_qr_data()
            qr_response = requests.post(
                f"{target_url}/api/qrdata",
                json=qr_data,
                timeout=2
            )
            print(f"QR: {qr_response.status_code}, {qr_response.text}")

        except Exception as e:
            print(f"Error: {str(e)}")
        time.sleep(interval)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Using default localhost:5000")
        target = "http://localhost:5000" #for local
        #target = "http://34.88.197.179:5000/"  #for cloud
    else:
        target = sys.argv[1]

    try:
        interval = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
        print(f"Starting sensor spammer to {target} (interval: {interval}s)")
        print("Press Ctrl+C to stop")
        spam_data(target, interval)
    except KeyboardInterrupt:
        print("\nStopped by user")