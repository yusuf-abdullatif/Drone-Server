import requests
import random
import time
import sys
from datetime import datetime


def generate_random_sensor_data():
    """Generates a dictionary of random sensor data."""
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
    """Generates a dictionary with a random QR code reading."""
    return {
        "last_qr_reading": f"QR_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    }


def get_arm_status(target_url):
    """
    Fetches the latest data, including the arming status, from the backend.
    Returns the 'armed' status as a boolean.
    """
    try:
        response = requests.get(f"{target_url}/api/latest", timeout=2)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        return data.get('armed', False)  # Default to False if 'armed' key is missing
    except requests.exceptions.RequestException as e:
        print(f"Error fetching arm status: {e}")
        return None  # Indicate failure to fetch status


def spam_data(target_url, interval=1):
    """
    Continuously sends sensor and QR data, and fetches arming status.
    Args:
        target_url (str): The base URL of the Flask application (e.g., "http://localhost:5000").
        interval (float): The time in seconds to wait between data sends.
    """
    print(f"Starting sensor spammer to {target_url} (interval: {interval}s)")
    print("Press Ctrl+C to stop")
    while True:
        try:
            # Send sensor data
            sensor_data = generate_random_sensor_data()
            sensor_response = requests.post(
                f"{target_url}/api/data",
                json=sensor_data,
                timeout=2
            )
            print(f"Sensor Data Sent: {sensor_response.status_code} - {sensor_response.text.strip()}")

            # Send QR data
            qr_data = generate_qr_data()
            qr_response = requests.post(
                f"{target_url}/api/qrdata",
                json=qr_data,
                timeout=2
            )
            print(f"QR Data Sent: {qr_response.status_code} - {qr_response.text.strip()}")

            # Get and display arm status
            armed_status = get_arm_status(target_url)
            if armed_status is not None:
                print(f"System Status: {'ARMED' if armed_status else 'DISARMED'}")
            else:
                print("System Status: Could not retrieve")

        except requests.exceptions.ConnectionError:
            print(f"Connection Error: Could not connect to {target_url}. Is the Flask app running?")
        except requests.exceptions.Timeout:
            print("Timeout Error: Request took too long.")
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP Error: {http_err} - {http_err.response.text}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

        print("-" * 30)  # Separator for readability
        time.sleep(interval)


if __name__ == "__main__":
    # Determine the target URL from command line arguments or default
    if len(sys.argv) < 2:
        print("Usage: python sensor_spammer.py <target_url> [interval_seconds]")
        print("Example: python sensor_spammer.py http://localhost:5000 0.5")
        print("Using default: http://localhost:5000")
        target = "http://localhost:5000"  # Default for local development
        # target = "http://34.88.197.179:5000"  # Example for cloud deployment
    else:
        target = sys.argv[1]

    # Determine the interval from command line arguments or default
    try:
        interval = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
    except ValueError:
        print("Invalid interval. Using default 0.5 seconds.")
        interval = 0.5

    try:
        spam_data(target, interval)
    except KeyboardInterrupt:
        print("\nStopped by user (Ctrl+C)")
    except Exception as final_e:
        print(f"Script terminated due to error: {final_e}")
