import cv2
import requests
import time
import threading
import io  # Import io for BytesIO

# --- Configuration ---
# Set this to the URL of your running Flask application.
# Use http://localhost:5000 if running locally, or your server's public IP.
#SERVER_URL = "http://34.88.197.179:5000"  # Use your cloud server URL
SERVER_URL = "http://localhost:5000"
VIDEO_ENDPOINT = f"{SERVER_URL}/api/video"

# --- Camera Settings ---
FRAME_WIDTH = 320
FRAME_HEIGHT = 240
FPS = 10
JPEG_QUALITY = 70  # 0-100, higher is better quality

# Boundary for the multipart stream
# This must match the boundary Flask expects in routes.py
# (though routes.py dynamically extracts it, consistent clients help)
MJPEG_BOUNDARY = "frame"  # This is the boundary used in your curl command


def generate_mjpeg_stream(camera_capture, frame_width, frame_height, fps, jpeg_quality):
    """
    Generator function to capture frames and format them as an MJPEG stream.
    Yields each frame as a byte string formatted for multipart/x-mixed-replace.
    """
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality]

    try:
        while True:
            ret, frame = camera_capture.read()
            if not ret:
                print("Warning: Dropped frame from camera, continuing...")
                time.sleep(0.01)  # Small sleep to prevent busy-waiting
                continue

            _, buffer = cv2.imencode('.jpg', frame, encode_param)
            frame_bytes = buffer.tobytes()

            # Construct the multipart part for this frame
            yield (b'--%s\r\n' % MJPEG_BOUNDARY.encode('utf-8') +
                   b'Content-Type: image/jpeg\r\n' +
                   b'Content-Length: %d\r\n\r\n' % len(frame_bytes) +
                   frame_bytes + b'\r\n')

            time.sleep(1 / fps)  # Control frame rate

    except KeyboardInterrupt:
        print("\nStopping MJPEG stream generation.")
    except Exception as e:
        print(f"Error during MJPEG stream generation: {e}")
    finally:
        camera_capture.release()


def send_camera_feed():
    """
    Captures video from the default camera and sends it as a continuous
    multipart/x-mixed-replace stream to the Flask server endpoint.
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

    print(f"Sending continuous MJPEG stream to: {VIDEO_ENDPOINT}")
    print("Press Ctrl+C to stop.")

    # Prepare headers for the continuous multipart stream
    headers = {
        'Content-Type': f'multipart/x-mixed-replace; boundary={MJPEG_BOUNDARY}'
    }

    try:
        # Use a session for persistent connection if sending many requests,
        # but here we are sending a single, long-lived request
        # requests.post can take a generator as data, which is perfect for continuous streaming
        response = requests.post(
            VIDEO_ENDPOINT,
            data=generate_mjpeg_stream(cap, FRAME_WIDTH, FRAME_HEIGHT, FPS, JPEG_QUALITY),
            headers=headers,
            stream=True,  # Important: keep the connection alive for streaming response
            timeout=None  # Important: No timeout for a long-lived stream unless an inactivity timeout is desired
        )
        # Check if the server responded immediately with an error (e.g., 400 Bad Request)
        if response.status_code != 200:
            print(f"Server returned status {response.status_code}: {response.text}")
        else:
            print("Successfully connected to video endpoint. Stream should be active.")
            # Read response content to keep the connection open and handle potential server-side errors
            for chunk in response.iter_content(chunk_size=4096):
                # We don't expect content back, but reading keeps the connection alive
                pass

    except requests.exceptions.ConnectionError as e:
        print(
            f"Connection error: Could not connect to the server at {VIDEO_ENDPOINT}. Is the server running and accessible?")
        print(e)
    except requests.exceptions.Timeout as e:
        print(f"Timeout error: Server took too long to respond. {e}")
    except requests.exceptions.RequestException as e:
        print(f"An unexpected request error occurred: {e}")
    except KeyboardInterrupt:
        print("\nStopping camera feed.")
    finally:
        # The generator will release the camera when it's done or interrupted
        print("Camera feed process finished.")


if __name__ == "__main__":
    send_camera_feed()
