import cv2
import requests
import time

#SERVER_URL = "http://localhost:5000"
SERVER_URL = "http://34.88.248.153:5000"

def send_camera_feed():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Encode frame
            _, buffer = cv2.imencode('.jpg', frame)

            # Send to cloud
            requests.post(
                f"{SERVER_URL}/api/video",
                data=buffer.tobytes(),
                headers={'Content-Type': 'application/octet-stream'}
            )

            time.sleep(0.033)  # ~30 FPS
    finally:
        cap.release()


if __name__ == "__main__":
    send_camera_feed()