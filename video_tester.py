import cv2
import requests
import time

# --- Configuration ---
# Set this to the URL of your running Flask application.
# Use http://localhost:5000 if running locally, or your server's public IP.
#SERVER_URL = "http://34.88.197.179:5000"
SERVER_URL = "http://localhost:5000"
VIDEO_ENDPOINT = f"{SERVER_URL}/api/video"

# --- Camera Settings ---
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FPS = 30
JPEG_QUALITY = 70  # 0-100, higher is better quality


def send_camera_feed():
    """
    Captures video from the default camera, encodes it as JPEG,
    and sends it to the Flask server endpoint frame by frame.
    """
    print("Starting camera feed...")

    # Initialize video capture from the default camera (index 0)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open video stream.")
        return

    # Set camera properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    print(f"Sending video to: {VIDEO_ENDPOINT}")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            # Capture frame-by-frame
            ret, frame = cap.read()
            if not ret:
                print("Warning: Dropped frame, continuing...")
                continue

            # Encode the frame to JPEG format with specified quality
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY]
            _, buffer = cv2.imencode('.jpg', frame, encode_param)

            # Send the JPEG data in the body of a POST request
            try:
                response = requests.post(
                    VIDEO_ENDPOINT,
                    data=buffer.tobytes(),
                    headers={'Content-Type': 'application/octet-stream'},
                    timeout=1  # Add a timeout to prevent hanging
                )
                # You can optionally check the response status
                # if response.status_code != 200:
                #     print(f"Server returned status {response.status_code}")

            except requests.exceptions.RequestException as e:
                print(f"Error sending frame: {e}")

            # Wait for a short period to control the frame rate
            time.sleep(1 / FPS)

    except KeyboardInterrupt:
        print("\nStopping camera feed.")
    finally:
        # When everything is done, release the capture
        cap.release()
        print("Camera released.")


if __name__ == "__main__":
    send_camera_feed()
