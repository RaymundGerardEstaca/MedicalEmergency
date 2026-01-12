# Complete Project Documentation
## Network Configuration & Stream Viewer System

**Version:** 1.0.0  
**Last Updated:** January 12, 2026  
**Platform:** React Native (Expo) + FastAPI Backend

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [Frontend Application](#frontend-application)
6. [Backend System](#backend-system)
7. [Setup & Installation](#setup--installation)
8. [Configuration](#configuration)
9. [API Documentation](#api-documentation)
10. [Development Guide](#development-guide)
11. [Deployment](#deployment)
12. [Troubleshooting](#troubleshooting)

---

## 🎯 Project Overview

A comprehensive **CCTV Network Configuration and Stream Viewer** application that enables users to:
- Discover and configure IP cameras on local networks
- Provision WiFi settings to cameras via BLE or SoftAP
- View live HLS video streams with low latency
- Manage multiple camera devices
- Receive critical alarm notifications

### Key Features

#### 🔧 Network & Edge Configuration (Module A)
- **Camera Configuration Dashboard** - Configure camera name, IP, RTSP credentials
- **Network Discovery** - Automatic LAN scanning to discover devices
- **Connection Testing** - Ping and RTSP validation

#### 📹 Mobile Stream Integration (Module C)
- **Adaptive Video Player** - HLS stream playback with expo-av
- **Stream State Management** - Loading, live, offline handling
- **Pull-to-Refresh** - Manual stream reload
- **Alert Snapshots** - Recent alert carousel with full-screen viewer

#### 🚨 Critical Alarm System (Module Z)
- **Full-Screen Alarm Modal** - Red/white flashing background (2Hz)
- **Slide-to-Dismiss Control** - iPhone-style slider to stop alarm

### Target Users
- Homeowners with security camera systems
- Small business owners
- Property managers
- Security system installers

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     MOBILE APPLICATION                           │
│                    (React Native + Expo)                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌───────────────┐  ┌────────────────┐  ┌──────────────────┐  │
│  │  Screens      │  │  Components    │  │  Services        │  │
│  │  - Login      │  │  - AlarmModal  │  │  - BackendAPI    │  │
│  │  - DeviceList │  │  - DeviceItem  │  │  - BLE           │  │
│  │  - Stream     │  │  - Scanner     │  │  - WiFi          │  │
│  │  - Config     │  │  - Progress    │  │  - Storage       │  │
│  └───────────────┘  └────────────────┘  └──────────────────┘  │
│                                                                   │
└───────────────────────────┬───────────────────────────────────┘
                            │
                            │ HTTPS/WebSocket
                            │
┌───────────────────────────▼───────────────────────────────────┐
│                     BACKEND SERVER                             │
│                     (FastAPI + Uvicorn)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  API Endpoints (REST)                                       │ │
│  │  - /api/auth/*        - Authentication                      │ │
│  │  - /api/devices/*     - Device Management                   │ │
│  │  - /api/stream/*      - Stream Control                      │ │
│  │  - /api/wifi/*        - WiFi Validation                     │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Streaming Services                                         │ │
│  │  - RTSP → HLS Transcoding (FFmpeg)                         │ │
│  │  - WebSocket Frame Streaming (OpenCV)                      │ │
│  │  - Multi-camera Management                                  │ │
│  │  - Health Monitoring                                        │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Data Storage                                               │ │
│  │  - devices_db.json   - Device registry                      │ │
│  │  - users_db.json     - User accounts                        │ │
│  │  - hls_output/       - HLS stream files                     │ │
│  │  - logs/             - System logs                          │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
└───────────────────────────┬───────────────────────────────────┘
                            │
                            │ RTSP Protocol
                            │
┌───────────────────────────▼───────────────────────────────────┐
│                     IP CAMERAS                                 │
│            (RTSP/ONVIF Compatible Devices)                     │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Authentication Flow**
   ```
   Mobile → POST /api/auth/login → Backend
   Backend → Validate credentials → Return JWT token
   Mobile → Store token in SecureStore → Use for all requests
   ```

2. **Device Discovery Flow**
   ```
   Mobile → Scan BLE devices → Discover cameras
   Mobile → POST /api/devices/register → Backend
   Backend → Store device info → Return device ID
   ```

3. **Stream Viewing Flow**
   ```
   Mobile → POST /api/stream/start → Backend
   Backend → Start FFmpeg transcoding → Generate HLS playlist
   Backend → WebSocket frames (optional) → Mobile
   Mobile → Fetch .m3u8 playlist → Play in expo-av
   ```

---

## 🛠️ Technology Stack

### Frontend (Mobile App)

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| **Framework** | React Native | 0.76.9 | Cross-platform mobile development |
| **Build Tool** | Expo | ~52.0.0 | Development and build pipeline |
| **Language** | TypeScript | ~5.3.3 | Type-safe development |
| **Navigation** | React Navigation | ^6.1.18 | Screen routing |
| **Video Playback** | expo-av | ~15.0.0 | HLS stream playback |
| **Secure Storage** | expo-secure-store | ~14.0.0 | Credential encryption |
| **Networking** | @react-native-community/netinfo | ^11.4.1 | Network status monitoring |
| **BLE** | react-native-ble-plx | ^3.5.0 | Bluetooth Low Energy communication |
| **WiFi** | react-native-wifi-reborn | ^4.13.6 | WiFi configuration |
| **Authentication** | @react-native-google-signin | ^16.0.0 | Google OAuth integration |

### Backend (Server)

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| **Framework** | FastAPI | >=0.110.0 | Modern async web framework |
| **Server** | Uvicorn | >=0.29.0 | ASGI server |
| **Video Processing** | OpenCV | >=4.9.0.80 | Frame capture and processing |
| **Streaming** | FFmpeg | 8.0.1 | RTSP to HLS transcoding |
| **Async** | asyncio | Built-in | Async operations |
| **WebSocket** | websockets | >=12.0 | Real-time frame streaming |
| **Data Validation** | Pydantic | >=2.7.0 | Request/response validation |

### Infrastructure

- **Hosting:** Self-hosted or cloud (AWS, DigitalOcean, etc.)
- **Video Storage:** Local filesystem (HLS segments)
- **Database:** JSON files (lightweight, no DB required)
- **Logs:** File-based logging with rotation

---

## 📁 Project Structure

```
MobileApp Research/
├── 📱 FRONTEND (React Native)
│   ├── App.tsx                          # Main app entry with navigation
│   ├── app.json                         # Expo configuration
│   ├── package.json                     # NPM dependencies
│   ├── tsconfig.json                    # TypeScript configuration
│   │
│   ├── src/
│   │   ├── screens/                     # Application screens
│   │   │   ├── SplashScreen.tsx         # Initial loading screen
│   │   │   ├── LoginScreen.tsx          # User authentication
│   │   │   ├── DevicesListScreen.tsx    # List of configured cameras
│   │   │   ├── DeviceDiscoveryScreen.tsx # BLE camera discovery
│   │   │   ├── WiFiProvisioningScreen.tsx # BLE WiFi configuration
│   │   │   ├── SoftAPProvisioningScreen.tsx # SoftAP WiFi config
│   │   │   ├── CameraConfigScreen.tsx   # Camera settings editor
│   │   │   └── StreamViewerScreen.tsx   # Live stream viewer
│   │   │
│   │   ├── components/                  # Reusable UI components
│   │   │   ├── AlarmModal.tsx           # Critical alarm overlay
│   │   │   ├── DeviceListItem.tsx       # Camera list item
│   │   │   ├── NetworkScanner.tsx       # LAN scanning component
│   │   │   ├── ScanProgress.tsx         # Scan progress indicator
│   │   │   └── GoogleLogo.tsx           # Google sign-in logo
│   │   │
│   │   ├── services/                    # Business logic services
│   │   │   ├── BackendAPIService.ts     # Backend HTTP client
│   │   │   ├── BLEProvisioningService.ts # BLE communication
│   │   │   ├── SoftAPProvisioningService.ts # SoftAP communication
│   │   │   ├── SmartConfigService.ts    # ESP SmartConfig protocol
│   │   │   ├── WiFiDetectionService.ts  # WiFi network detection
│   │   │   ├── NetworkDeviceDiscoveryService.ts # LAN scanner
│   │   │   ├── DeviceStorageService.ts  # Local device storage
│   │   │   └── LoggerService.ts         # Logging utility
│   │   │
│   │   └── types/                       # TypeScript type definitions
│   │       ├── index.ts                 # Main type exports
│   │       ├── env.d.ts                 # Environment types
│   │       └── react-native.d.ts        # RN type extensions
│   │
│   ├── android/                         # Android native code
│   ├── ios/                             # iOS native code (if exists)
│   ├── assets/                          # Images, fonts, etc.
│   └── scripts/                         # Build and utility scripts
│
├── 🖥️ BACKEND (FastAPI)
│   ├── backend/
│   │   ├── main_backend.py              # Main FastAPI application
│   │   ├── rtsp_stream_service.py       # Streaming service
│   │   ├── logger_service.py            # Logging configuration
│   │   ├── run_backend.py               # Backend launcher script
│   │   ├── requirements.txt             # Python dependencies
│   │   │
│   │   ├── devices_db.json              # Device registry database
│   │   ├── users_db.json                # User accounts database
│   │   │
│   │   ├── venv/                        # Python virtual environment
│   │   ├── hls_output/                  # HLS stream output directory
│   │   ├── logs/                        # Application logs
│   │   ├── recordings/                  # Stream recordings (if enabled)
│   │   │
│   │   └── test-backend-api.sh/ps1      # API testing scripts
│   │
│   └── docs/                            # Documentation
│       ├── PROJECT-DOCUMENTATION.md     # This file
│       ├── API-REFERENCE.md             # API endpoints documentation
│       ├── FRONTEND-GUIDE.md            # Frontend development guide
│       ├── BACKEND-GUIDE.md             # Backend development guide
│       ├── DEPLOYMENT-GUIDE.md          # Deployment instructions
│       ├── HOW-TO-RUN.md                # Quick start guide
│       ├── SETUP.md                     # Initial setup
│       └── QUICK-START.md               # Quick reference
│
└── 📝 Configuration Files
    ├── .github/
    │   └── copilot-instructions.md      # GitHub Copilot instructions
    ├── .gitignore                       # Git ignore rules
    ├── .vscode/                         # VS Code settings
    ├── jest.config.js                   # Jest test configuration
    ├── babel.config.js                  # Babel transpiler config
    └── README.md                        # Project readme
```

---

## 📱 Frontend Application

### Screens Overview

#### 1. **SplashScreen** (`SplashScreen.tsx`)
- **Purpose:** Initial loading screen with app logo
- **Duration:** 2-3 seconds
- **Auto-navigation:** → LoginScreen (if not authenticated) or DevicesListScreen

#### 2. **LoginScreen** (`LoginScreen.tsx`)
- **Purpose:** User authentication
- **Features:**
  - Email/Password login
  - Google Sign-In (OAuth)
  - Registration link
  - "Remember Me" option
- **API Calls:**
  - `POST /api/auth/login`
  - `POST /api/auth/register`
- **Storage:** JWT token saved to SecureStore

#### 3. **DevicesListScreen** (`DevicesListScreen.tsx`)
- **Purpose:** Display all configured cameras
- **Features:**
  - List of devices with status indicators
  - "Add Camera" button → DeviceDiscoveryScreen
  - Tap device → StreamViewerScreen
  - Pull-to-refresh to update statuses
  - Device heartbeat polling
- **API Calls:**
  - `GET /api/devices`
  - `POST /api/devices/{id}/heartbeat`

#### 4. **DeviceDiscoveryScreen** (`DeviceDiscoveryScreen.tsx`)
- **Purpose:** Discover new cameras via BLE
- **Features:**
  - BLE scanning for nearby devices
  - Device list with signal strength
  - Connect button → WiFiProvisioningScreen
  - SoftAP fallback option
- **Services Used:**
  - `BLEProvisioningService`
  - `NetworkDeviceDiscoveryService`

#### 5. **WiFiProvisioningScreen** (`WiFiProvisioningScreen.tsx`)
- **Purpose:** Configure camera WiFi via BLE
- **Features:**
  - WiFi network selection
  - Password input
  - Send credentials to camera via BLE
  - Connection progress indicator
- **BLE Protocol:**
  - Write WiFi SSID to characteristic
  - Write password to characteristic
  - Receive connection confirmation

#### 6. **SoftAPProvisioningScreen** (`SoftAPProvisioningScreen.tsx`)
- **Purpose:** Configure camera WiFi via SoftAP mode
- **Features:**
  - Connect to camera's WiFi hotspot
  - HTTP-based credential sending
  - Progress monitoring
- **Flow:**
  1. User connects to camera's AP (e.g., "ESP32-CAM-XXXX")
  2. App sends credentials via HTTP POST
  3. Camera connects to target WiFi
  4. App reconnects to home WiFi

#### 7. **CameraConfigScreen** (`CameraConfigScreen.tsx`)
- **Purpose:** Configure camera settings
- **Features:**
  - Device name input
  - IP address configuration
  - RTSP URL and credentials
  - Connection test button
  - Save configuration
- **Validation:**
  - IP address format check
  - RTSP URL validation
  - Ping test
- **API Calls:**
  - `PUT /api/devices/{id}`
  - `POST /api/stream/check-connectivity`

#### 8. **StreamViewerScreen** (`StreamViewerScreen.tsx`)
- **Purpose:** View live camera stream
- **Features:**
  - HLS video playback with expo-av
  - Loading state with spinner
  - "LIVE" badge with flashing indicator
  - Mute/unmute toggle
  - Pull-to-refresh stream reload
  - Alert snapshots carousel
  - Error handling with retry
- **API Calls:**
  - `POST /api/stream/start`
  - `GET /api/stream/{id}/status`
  - `POST /api/stream/stop`

### Services

#### BackendAPIService (`BackendAPIService.ts`)
HTTP client for backend communication.

```typescript
class BackendAPIService {
  private baseURL: string;
  private authToken: string | null;

  // Authentication
  async login(email: string, password: string): Promise<LoginResponse>
  async register(email: string, password: string, name: string): Promise<RegisterResponse>
  async logout(): Promise<void>

  // Device Management
  async getDevices(): Promise<Device[]>
  async getDevice(deviceId: string): Promise<Device>
  async registerDevice(device: DeviceRegister): Promise<Device>
  async updateDevice(deviceId: string, updates: DeviceUpdate): Promise<Device>
  async deleteDevice(deviceId: string): Promise<void>
  async deviceHeartbeat(deviceId: string): Promise<HeartbeatResponse>

  // Streaming
  async startStream(url: string, streamId?: string): Promise<StreamStartResponse>
  async stopStream(streamId: string): Promise<void>
  async getStreamStatus(streamId: string): Promise<StreamStatus>
  async checkConnectivity(url: string): Promise<ConnectivityResult>

  // WiFi
  async validateWiFi(ssid: string): Promise<ValidationResult>
}
```

#### BLEProvisioningService (`BLEProvisioningService.ts`)
Bluetooth Low Energy communication for WiFi provisioning.

```typescript
class BLEProvisioningService {
  // Scanning
  async startScan(callback: (device: BLEDevice) => void): Promise<void>
  async stopScan(): Promise<void>

  // Connection
  async connect(deviceId: string): Promise<void>
  async disconnect(): Promise<void>

  // Provisioning
  async sendWiFiCredentials(ssid: string, password: string): Promise<boolean>
  async getConnectionStatus(): Promise<ConnectionStatus>

  // Characteristics
  private async writeCharacteristic(serviceUUID: string, charUUID: string, data: string): Promise<void>
  private async readCharacteristic(serviceUUID: string, charUUID: string): Promise<string>
}
```

#### DeviceStorageService (`DeviceStorageService.ts`)
Local device persistence using SecureStore.

```typescript
class DeviceStorageService {
  // Devices
  async saveDevice(device: CCTVDevice): Promise<void>
  async getDevice(deviceId: string): Promise<CCTVDevice | null>
  async getAllDevices(): Promise<CCTVDevice[]>
  async deleteDevice(deviceId: string): Promise<void>
  async updateDevice(deviceId: string, updates: Partial<CCTVDevice>): Promise<void>

  // Auth Token
  async saveAuthToken(token: string): Promise<void>
  async getAuthToken(): Promise<string | null>
  async deleteAuthToken(): Promise<void>

  // Camera Configs
  async saveCameraConfig(config: CameraConfig): Promise<void>
  async getCameraConfig(deviceId: string): Promise<CameraConfig | null>
}
```

### Components

#### AlarmModal (`AlarmModal.tsx`)
Critical alarm overlay with slide-to-dismiss.

**Props:**
```typescript
interface AlarmModalProps {
  visible: boolean;
  onDismiss: () => void;
  snapshot?: string;  // Base64 image
  timestamp: Date;
  detectedObject: string;
}
```

**Features:**
- Red/white flashing background (2Hz)
- Large warning text
- Snapshot preview
- Slide-to-dismiss control (iPhone-style)
- Siren sound and vibration

#### DeviceListItem (`DeviceListItem.tsx`)
Camera device list item component.

**Props:**
```typescript
interface DeviceListItemProps {
  device: CCTVDevice;
  onPress: () => void;
  onLongPress?: () => void;
}
```

**Display:**
- Camera name and IP
- Online/Offline status indicator
- Signal strength icon
- Last seen timestamp

#### NetworkScanner (`NetworkScanner.tsx`)
LAN network scanner component.

**Features:**
- Scan local network for devices
- Display discovered devices with IPs
- Filter by device type
- Auto-fill IP address on selection

---

## 🖥️ Backend System

### Main Application (`main_backend.py`)

**FastAPI app with comprehensive logging, authentication, and streaming.**

#### Core Components

1. **Logging System**
   - Sensitive data masking (IPs, tokens, passwords)
   - Console and file handlers
   - Structured log format
   - Separate logs for: backend, access, API

2. **Middleware**
   - CORS (allow all origins)
   - Request/Response logging
   - Performance monitoring (slow request detection)

3. **Data Storage**
   - JSON file-based (no database required)
   - In-memory caching
   - Auto-save on changes

4. **Authentication**
   - SHA256 password hashing
   - JWT-like token generation
   - Token expiration (24 hours)
   - Bearer token validation

### Streaming Service (`rtsp_stream_service.py`)

**Production-grade RTSP to HLS transcoding with OpenCV fallback.**

#### Architecture

```python
class EnhancedStreamService:
    def __init__(self):
        self.streams: Dict[str, StreamSession] = {}
        self.lock = threading.Lock()

    def start_stream(self, url: str, stream_id: str, mode: StreamMode) -> bool
    def stop_stream(self, stream_id: str) -> bool
    def stop_all(self) -> None
    def get_stream_status(self, stream_id: str) -> Dict
    def get_all_statuses(self) -> List[Dict]
    def get_frame(self, stream_id: str) -> Optional[bytes]  # For WebSocket
```

#### Stream Modes

1. **HLS Mode** (`mode='hls'`)
   - FFmpeg transcoding to HLS
   - Low latency (2s segments)
   - Suitable for mobile playback
   - Files: `{stream_id}/stream.m3u8`

2. **WebSocket Mode** (`mode='websocket'`)
   - OpenCV frame capture
   - Real-time JPEG frames
   - Lower latency than HLS
   - Higher bandwidth

3. **Both Mode** (`mode='both'`)
   - HLS + WebSocket simultaneously
   - Best compatibility

#### FFmpeg Command

```bash
ffmpeg -rtsp_transport tcp \
       -i {rtsp_url} \
       -c:v libx264 -preset ultrafast -tune zerolatency \
       -c:a aac -b:a 128k \
       -f hls -hls_time 2 -hls_list_size 3 \
       -hls_flags delete_segments+append_list \
       -hls_segment_filename "{output_dir}/segment_%03d.ts" \
       "{output_dir}/stream.m3u8"
```

**Settings:**
- TCP transport (reliability)
- Ultrafast preset (low latency)
- 2-second segments
- 3 segments in playlist
- Auto-delete old segments

#### Health Monitoring

```python
class StreamSession:
    def update_health(self):
        if self.is_ffmpeg_alive():
            self.health_status = 'healthy'
        else:
            self.health_status = 'unhealthy'
            self.restart_attempts += 1
            if self.restart_attempts < MAX_RESTART:
                self.restart_stream()
```

---

## 🚀 Setup & Installation

### Prerequisites

**System Requirements:**
- Windows 10/11, macOS 11+, or Linux
- Node.js 18+ and npm
- Python 3.9+ with pip
- Android Studio (for Android) or Xcode (for iOS)
- FFmpeg 4.4+ installed and in PATH

**Install FFmpeg:**

**Windows:**
```powershell
# Download from https://ffmpeg.org/download.html
# Extract to C:\ffmpeg
# Add C:\ffmpeg\bin to PATH
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt update
sudo apt install ffmpeg
```

### Frontend Setup

```bash
# 1. Navigate to project root
cd "d:\MobileApp Research"

# 2. Install dependencies
npm install

# 3. Install Expo CLI globally (if not installed)
npm install -g expo-cli

# 4. Start development server
npx expo start

# 5. Run on device/emulator
# Press 'a' for Android
# Press 'i' for iOS
# Or scan QR code with Expo Go app
```

### Backend Setup

```bash
# 1. Navigate to backend directory
cd "d:\MobileApp Research\backend"

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run backend server
python main_backend.py

# Or use the launcher script:
python run_backend.py
```

**Backend will start on:** `http://localhost:8000`

### Verify Installation

```bash
# Check backend health
curl http://localhost:8000/api/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2026-01-12T10:30:00.000Z",
  "version": "4.0.0",
  "uptime_seconds": 45
}
```

---

## ⚙️ Configuration

### Frontend Configuration

**Backend URL** (`src/services/BackendAPIService.ts`):
```typescript
private baseURL = 'http://192.168.1.100:8000';  // Change to your server IP
```

**App Configuration** (`app.json`):
```json
{
  "expo": {
    "name": "Network Config & Stream Viewer",
    "slug": "network-config-stream-viewer",
    "version": "1.0.0",
    "orientation": "portrait",
    "icon": "./assets/icon.png",
    "splash": {
      "image": "./assets/splash.png",
      "resizeMode": "contain",
      "backgroundColor": "#000000"
    },
    "android": {
      "package": "com.yourcompany.cctvapp",
      "permissions": [
        "ACCESS_FINE_LOCATION",
        "ACCESS_COARSE_LOCATION",
        "BLUETOOTH",
        "BLUETOOTH_ADMIN",
        "BLUETOOTH_SCAN",
        "BLUETOOTH_CONNECT",
        "ACCESS_WIFI_STATE",
        "CHANGE_WIFI_STATE",
        "INTERNET"
      ]
    }
  }
}
```

### Backend Configuration

**Environment Variables** (`.env` file):
```bash
# Server
HOST=0.0.0.0
PORT=8000

# Directories
HLS_OUTPUT_DIR=./hls_output
RECORDINGS_DIR=./recordings
LOG_DIR=./logs

# Streaming
HLS_SEGMENT_DURATION=2
HLS_LIST_SIZE=3
MAX_RECONNECT_ATTEMPTS=10

# FFmpeg
FFMPEG_PATH=/path/to/ffmpeg
FFPROBE_PATH=/path/to/ffprobe
```

**FFmpeg Path** (`rtsp_stream_service.py`):
```python
# Update these paths if FFmpeg is not in PATH
FFMPEG_WINDOWS_PATH = r'C:\ffmpeg\bin\ffmpeg.exe'
FFPROBE_WINDOWS_PATH = r'C:\ffmpeg\bin\ffprobe.exe'
```

---

## 📚 API Documentation

See [API-REFERENCE.md](./API-REFERENCE.md) for complete API documentation.

### Quick Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/auth/register` | POST | Register new user |
| `/api/auth/login` | POST | User login |
| `/api/devices` | GET | List all devices |
| `/api/devices/register` | POST | Register device |
| `/api/stream/start` | POST | Start stream |
| `/ws/stream/{id}` | WS | WebSocket stream |
| `/hls/{id}/stream.m3u8` | GET | HLS playlist |

---

## 🧑‍💻 Development Guide

### Frontend Development

**Running Tests:**
```bash
npm test
```

**Building for Production:**
```bash
# Android
eas build --platform android

# iOS
eas build --platform ios
```

**Debugging:**
- Use React Native Debugger
- Enable Remote JS Debugging in Expo
- Check console logs in Metro bundler

### Backend Development

**Running Tests:**
```bash
# Test API endpoints
bash test-backend-api.sh
# Or
powershell ./test-backend-api.ps1
```

**Development Server:**
```bash
# With auto-reload
uvicorn main_backend:app --reload --host 0.0.0.0 --port 8000
```

**Logging:**
- Logs in `backend/logs/`
- `backend.log` - Main application logs
- `access.log` - HTTP request logs
- `api.log` - API endpoint logs

---

## 🚢 Deployment

### Backend Deployment

**Option 1: Docker**
```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["python", "main_backend.py"]
```

**Option 2: Systemd Service**
```ini
[Unit]
Description=CCTV Backend Service
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/cctv-backend
ExecStart=/opt/cctv-backend/venv/bin/python main_backend.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### Frontend Deployment

**Build APK:**
```bash
eas build --platform android --profile production
```

**Build IPA:**
```bash
eas build --platform ios --profile production
```

---

## 🔧 Troubleshooting

### Common Issues

**1. FFmpeg not found**
```
Error: ffmpeg: command not found
```
**Solution:** Install FFmpeg and add to PATH

**2. RTSP connection timeout**
```
Error: Failed to connect to RTSP stream
```
**Solution:** 
- Check camera IP and credentials
- Verify network connectivity
- Use TCP transport: `rtsp://user:pass@ip:554/stream?tcp`

**3. BLE scanning fails**
```
Error: BLE scan failed
```
**Solution:**
- Check Android/iOS permissions
- Enable Bluetooth on device
- Ensure location services enabled (Android)

**4. HLS stream not playing**
```
Error: Cannot load m3u8
```
**Solution:**
- Check FFmpeg is running: `ps aux | grep ffmpeg`
- Verify HLS files exist: `ls backend/hls_output/{stream_id}/`
- Check CORS headers in backend

---

## 📞 Support

For issues, questions, or contributions:
- **GitHub Issues:** [Create an issue]
- **Documentation:** See `docs/` directory
- **Email:** support@example.com

---

## 📄 License

This project is proprietary software. All rights reserved.

---

**Last Updated:** January 12, 2026  
**Version:** 1.0.0  
**Authors:** Development Team
