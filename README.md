# Drone Telemetry and Video Streaming System

## Overview

This system provides a comprehensive solution for receiving, storing, and visualizing drone telemetry data and video streams in real-time. The backend is built with Python/Flask, using WebSockets for real-time communication and PostgreSQL for data persistence. The system includes:

- REST API endpoints for telemetry data submission
- WebSocket-based video streaming
- Database storage for historical telemetry data
- Web interface for data visualization

## System Architecture

### Components

1. **Backend Server**: Flask application with Socket.IO for real-time communication
2. **Database**: PostgreSQL for persistent storage of telemetry data
3. **Frontend**: Web interface (HTML/JS) for data visualization
4. **Client Tools**: Python scripts for testing (sensor data simulation and video streaming)

### Communication Flow

1. **Telemetry Data**:
   - Drone/client sends POST requests to `/api/data` with JSON payload
   - Server stores data in PostgreSQL database
   - Web interface can retrieve latest data via `/api/latest`

2. **Video Streaming**:
   - Drone/client sends video frames to `/api/video` as binary data
   - Server broadcasts frames to all connected WebSocket clients
   - Frames are encoded as base64 JPEG images

## Technical Specifications

### Backend Technologies

- **Python 3.x**
- **Flask** (Web framework)
- **Flask-SocketIO** (WebSocket support)
- **Flask-SQLAlchemy** (ORM)
- **PostgreSQL** (Database)
- **OpenCV** (Video processing)
- **Gunicorn** (WSGI server)
- **Gevent** (Asynchronous networking)

### API Endpoints

| Endpoint       | Method | Description                          |
|----------------|--------|--------------------------------------|
| `/`            | GET    | Web interface                        |
| `/api/data`    | POST   | Submit telemetry data                |
| `/api/latest`  | GET    | Retrieve latest telemetry data       |
| `/api/video`   | POST   | Submit video frame                   |

## Google Cloud Compute Engine Setup

### Prerequisites

1. Google Cloud account
2. Google Cloud SDK installed locally
3. Docker installed on local machine
4. Domain name (optional) for production deployment

### Deployment Steps

1. **Create Compute Engine Instance**
   - Navigate to Google Cloud Console
   - Create new VM instance with:
     - Machine type: e2-medium (or higher for production)
     - Boot disk: Ubuntu 20.04 LTS
     - Allow HTTP/HTTPS traffic

2. **Set Up Firewall Rules**
   - Allow inbound traffic on ports:
     - 5000 (Flask application)
     - 5432 (PostgreSQL - for internal communication only)

3. **Install Docker on VM**
   ```bash
   sudo apt-get update
   sudo apt-get install docker.io
   sudo systemctl start docker
   sudo systemctl enable docker
   ```

4. **Install Docker Compose**
   ```bash
   sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

5. **Clone Repository**
   ```bash
   git clone [your-repository-url]
   cd [repository-directory]
   ```

6. **Configure Environment**
   - Set up environment variables in `.env` file if needed
   - Ensure `DATABASE_URL` in `docker-compose.yml` matches your configuration

7. **Build and Deploy**
   ```bash
   sudo docker-compose build
   sudo docker-compose up -d
   ```

8. **Set Up Reverse Proxy (Optional for Production)**
   - Install Nginx:
     ```bash
     sudo apt-get install nginx
     ```
   - Configure Nginx as reverse proxy:
     ```bash
     sudo nano /etc/nginx/sites-available/yourdomain.com
     ```
     Add configuration:
     ```
     server {
         listen 80;
         server_name yourdomain.com;

         location / {
             proxy_pass http://localhost:5000;
             proxy_set_header Host $host;
             proxy_set_header X-Real-IP $remote_addr;
             proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
             proxy_set_header X-Forwarded-Proto $scheme;
         }

         location /socket.io {
             proxy_pass http://localhost:5000/socket.io;
             proxy_http_version 1.1;
             proxy_set_header Upgrade $http_upgrade;
             proxy_set_header Connection "upgrade";
             proxy_set_header Host $host;
         }
     }
     ```
   - Enable the configuration:
     ```bash
     sudo ln -s /etc/nginx/sites-available/yourdomain.com /etc/nginx/sites-enabled
     sudo nginx -t
     sudo systemctl restart nginx
     ```

9. **Set Up SSL (Optional)**
   - Install Certbot:
     ```bash
     sudo apt-get install certbot python3-certbot-nginx
     ```
   - Obtain SSL certificate:
     ```bash
     sudo certbot --nginx -d yourdomain.com
     ```

## Local Development Setup

### Prerequisites

1. Python 3.8+
2. PostgreSQL
3. Docker (optional)

### Installation

1. **Clone Repository**
   ```bash
   git clone [your-repository-url]
   cd [repository-directory]
   ```

2. **Set Up Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Database**
   - Install PostgreSQL
   - Create database and user:
     ```sql
     CREATE DATABASE dronedb;
     CREATE USER droneuser WITH PASSWORD 'drone_password';
     GRANT ALL PRIVILEGES ON DATABASE dronedb TO droneuser;
     ```

5. **Configure Environment Variables**
   Create `.env` file:
   ```
   DATABASE_URL=postgresql://droneuser:drone_password@localhost:5432/dronedb
   FLASK_APP=wsgi.py
   FLASK_ENV=development
   ```

6. **Initialize Database**
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

7. **Run Application**
   ```bash
   python wsgi.py
   ```

## Testing the System

### Using Test Scripts

1. **Sensor Data Simulator**
   ```bash
   python sensor_spammer.py [target_url] [interval]
   ```
   Example:
   ```bash
   python sensor_spammer.py http://localhost:5000 0.5
   ```

2. **Video Stream Tester**
   ```bash
   python video_tester.py
   ```

### Using Docker

1. **Build and Run**
   ```bash
   docker-compose up --build
   ```

2. **Access Application**
   - Web interface: `http://localhost:5000`
   - API endpoints: `http://localhost:5000/api/[endpoint]`

## Configuration Options

### Backend Configuration

- Modify `app/__init__.py` for Flask app configuration
- Adjust CORS settings in `routes.py` as needed
- Change database connection parameters in `docker-compose.yml` or `.env`

### Performance Tuning

1. **Video Streaming**
   - Adjust frame rate in `broadcast_frames()` function
   - Modify JPEG compression quality in `video_tester.py`

2. **Database**
   - Configure connection pooling in production
   - Implement database indexing for frequently queried fields

## Troubleshooting

### Common Issues

1. **Database Connection Problems**
   - Verify PostgreSQL is running
   - Check connection string in configuration
   - Ensure user has proper permissions

2. **Video Streaming Latency**
   - Reduce frame resolution in `video_tester.py`
   - Adjust compression quality
   - Check network bandwidth

3. **WebSocket Connection Issues**
   - Verify reverse proxy configuration (if using Nginx)
   - Check CORS settings
   - Ensure client is using compatible Socket.IO version


This README provides comprehensive documentation for setting up and running the drone telemetry and video streaming system. For additional support, please refer to the code comments or open an issue in the repository.
