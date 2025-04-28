
# Drone Telemetry System with Video Streaming

A complete system for collecting and visualizing drone sensor data (pitch/yaw/roll) and video streams, featuring:
- Python Flask backend with PostgreSQL database
- Docker containerization
- ESP32-CAM integration
- Web dashboard with real-time updates
- Multiple video streaming options

## 📦 System Architecture
```plaintext
ESP32 Drone
├── HTTP POST Sensor Data (JSON)
├── Video Streaming (MJPEG/RTSP)
│
Azure VM
├── Flask API (Python)
│   ├── PostgreSQL Database
│   ├── Redis (Optional)
│   └── Nginx Reverse Proxy
│
Web Client
├── Real-time Dashboard
├── Sensor Data Visualization
└── Live Video Feed
```

## 🛠️ Prerequisites

1. **Hardware**
   - ESP32-CAM module
   - FTDI programmer
   - WiFi network (2.4GHz)

2. **Software**
   - Docker & Docker Compose
   - Python 3.9+
   - Arduino IDE (for ESP32)
   - PostgreSQL client

## 🚀 Installation

### Backend Setup
```bash
# Clone repository
git clone https://github.com/yourusername/drone-telemetry-system.git
cd drone-telemetry-system

# Create environment file
cp .env.example .env
# Edit with your credentials
nano .env

# Build and start containers
docker-compose up --build -d

# Initialize database
docker-compose exec web flask db init
docker-compose exec web flask db migrate
docker-compose exec web flask db upgrade
```

### ESP32 Setup
1. Install required libraries:
   - ESP32 Board Package
   - `esp32-camera` & `HTTPClient`

2. Configure `esp32_code.ino`:
   ```cpp
   // WiFi Settings
   const char* ssid = "YOUR_WIFI";
   const char* password = "WIFI_PASSWORD";
   
   // Server Settings
   const char* serverUrl = "http://your-vm-ip:5000/api/data";
   const char* videoServerUrl = "http://your-vm-ip:5000/api/video";
   ```

3. Upload to ESP32-CAM via Arduino IDE

## ⚙️ Configuration

### Environment Variables (`.env`)
```ini
POSTGRES_USER=drone_user
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=drone_telemetry
FLASK_SECRET_KEY=your_flask_secret
```

### API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/data` | POST | Receive sensor data (JSON) |
| `/api/video` | POST | Receive video frames |
| `/video_feed` | GET | MJPEG video stream |
| `/` | GET | Web dashboard |

## 🌐 Web Interface
Access the dashboard at `http://your-vm-ip:5000`:
- Real-time sensor data table
- Live video feed (MJPEG)
- Auto-refreshing every 2 seconds

![Dashboard Preview](https://via.placeholder.com/800x600.png?text=Drone+Dashboard+Preview)

## 📹 Video Streaming Options

### 1. Basic MJPEG
```html
<img src="http://your-vm-ip:5000/video_feed" width="640" height="480">
```

### 2. RTSP (Recommended)
```yaml
# docker-compose.yml
rtsp_server:
  image: aler9/rtsp-simple-server
  ports:
    - "8554:8554"
    - "1935:1935"
```

ESP32 Code:
```cpp
// Use RTSP library instead of HTTP POST
rtsp.sendFrame(fb->buf, fb->len);
```

## 🔒 Security
1. **HTTPS Setup**
```bash
sudo certbot --nginx -d yourdomain.com
```

2. **API Authentication**
```python
# Enable in routes.py
@auth.login_required
def receive_data():
    # ...
```

## 🐛 Troubleshooting

**Common Issues**:
1. Database Connection Failures:
   ```bash
   docker-compose exec db psql -U drone_user -d drone_telemetry
   ```

2. Missing Camera Frames:
   ```cpp
   // Reduce image quality in ESP32 code
   config.frame_size = FRAMESIZE_QVGA;
   config.jpeg_quality = 15;
   ```

3. High Latency:
   - Enable hardware acceleration in Nginx
   - Use RTSP instead of MJPEG

## 📄 License
MIT License - See [LICENSE](LICENSE) for details

