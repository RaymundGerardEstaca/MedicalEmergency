# Network Configuration & Stream Viewer

A comprehensive **CCTV Network Configuration and Stream Viewer** system with React Native mobile app and FastAPI backend for discovering, configuring, and viewing IP camera streams.

---

## 📚 Complete Documentation

This project includes comprehensive documentation covering every aspect of the system:

### 📖 **[PROJECT-DOCUMENTATION.md](docs/PROJECT-DOCUMENTATION.md)**
**Complete project overview with architecture, tech stack, and setup**
- Project overview and features
- System architecture diagrams
- Technology stack details
- Complete project structure
- Frontend and backend components
- Setup and installation guides
- Configuration instructions
- Troubleshooting

### 📡 **[API-REFERENCE.md](docs/API-REFERENCE.md)**
**Complete REST API and WebSocket endpoint documentation**
- Authentication endpoints (register, login, logout)
- Device management API (CRUD operations)
- Streaming endpoints (start, stop, status)
- WebSocket streaming protocol
- HLS playlist structure
- Error codes and handling
- Rate limiting details
- Complete cURL examples

### 📱 **[FRONTEND-GUIDE.md](docs/FRONTEND-GUIDE.md)**
**React Native mobile application development guide**
- App architecture and navigation
- Screen-by-screen implementation
- Component library
- Service layer details
- State management patterns
- BLE and WiFi provisioning
- Video streaming with expo-av
- Styling guidelines

### 🖥️ **[BACKEND-GUIDE.md](docs/BACKEND-GUIDE.md)**
**FastAPI backend development guide**
- Backend architecture
- Streaming service implementation
- FFmpeg integration
- Authentication system
- Logging and monitoring
- Database management
- Performance optimization
- Common patterns

### 🚀 **[DEPLOYMENT-GUIDE.md](docs/DEPLOYMENT-GUIDE.md)**
**Production deployment for Linux, Windows, Docker, and Cloud**
- Linux server deployment (Ubuntu/Debian)
- Windows Server deployment
- Docker and Docker Compose
- AWS and Azure cloud deployment
- Nginx reverse proxy setup
- SSL/TLS configuration
- Security hardening
- Monitoring and backups

### 🎯 **[QUICK-START.md](docs/QUICK-START.md)**
Quick reference for common tasks

### ⚙️ **[SETUP.md](docs/SETUP.md)**
Initial development environment setup

### 🏃 **[HOW-TO-RUN.md](docs/HOW-TO-RUN.md)**
Step-by-step instructions to run the project

---

## 🚀 Quick Start

### Backend (FastAPI Server)

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (first time only)
python -m venv venv

# Activate virtual environment
# Windows Command Prompt:
venv\Scripts\activate

# Windows Git Bash/MINGW:
source venv/Scripts/activate

# Linux/Mac:
source venv/bin/activate

# Install dependencies (first time only)
pip install -r requirements.txt

# Run server
python main_backend.py
```

**Server runs on:** `http://localhost:8000`

### Frontend (React Native App)

```bash
# Install dependencies
npm install

# Start Expo development server
npx expo start

# Run on Android/iOS
# Press 'a' for Android or 'i' for iOS
```

---

## 🎯 Features

### 📹 **Camera Configuration**
- Network discovery and LAN scanning
- BLE and SoftAP WiFi provisioning
- RTSP connection testing
- Secure credential storage

### 🎬 **Video Streaming**
- RTSP to HLS transcoding with FFmpeg
- Low-latency WebSocket streaming
- Adaptive video player
- Multi-camera support

### 🚨 **Alarm System**
- Critical alarm notifications
- Full-screen alarm modal
- Slide-to-dismiss control
- Alert snapshots carousel

### 🔐 **Security**
- JWT-based authentication
- Encrypted credential storage
- Sensitive data masking in logs
- HTTPS/TLS support

---

## 📦 Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Mobile App** | React Native + Expo | Cross-platform mobile |
| **Backend** | FastAPI + Uvicorn | REST API server |
| **Streaming** | FFmpeg + OpenCV | RTSP to HLS transcoding |
| **Authentication** | JWT Tokens | Secure user auth |
| **Storage** | JSON Files | Lightweight database |
| **Video Player** | expo-av | HLS playback |
| **BLE** | react-native-ble-plx | Bluetooth provisioning |

---

## 📋 Prerequisites

**Backend:**
- Python 3.9+
- FFmpeg 4.4+
- 4GB RAM minimum

**Frontend:**
- Node.js 20.19.4+ (recommended: use latest LTS version)
- npm 10+ or yarn
- Android Studio or Xcode

> **Note:** While Node.js 20.19.1 works, 20.19.4+ is recommended to avoid engine warnings from `@react-native-community/cli`.

---

## 🛠️ Installation

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Choose based on your shell:
venv\Scripts\activate              # Windows CMD
source venv/Scripts/activate       # Git Bash/MINGW
source venv/bin/activate           # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run server
python main_backend.py
```

### 2. Frontend Setup

```bash
npm install
npx expo start
```

See **[SETUP.md](docs/SETUP.md)** for detailed instructions.

---

## 📖 Documentation Index

| Document | Description | Use Case |
|----------|-------------|----------|
| **PROJECT-DOCUMENTATION** | Complete system overview | Understanding the entire project |
| **API-REFERENCE** | REST API documentation | Backend integration |
| **FRONTEND-GUIDE** | Mobile app development | Frontend development |
| **BACKEND-GUIDE** | Server development | Backend development |
| **DEPLOYMENT-GUIDE** | Production deployment | Deploying to production |
| **QUICK-START** | Quick reference | Getting started fast |
| **SETUP** | Environment setup | First-time setup |
| **HOW-TO-RUN** | Run instructions | Daily development |

---

## 🏗️ Project Structure

```
d:\MobileApp Research/
├── 📱 Frontend (React Native)
│   ├── src/screens/          # App screens
│   ├── src/components/       # Reusable components
│   ├── src/services/         # Business logic
│   └── App.tsx              # Main app entry
│
├── 🖥️ Backend (FastAPI)
│   ├── backend/
│   │   ├── main_backend.py          # FastAPI app
│   │   ├── rtsp_stream_service.py   # Streaming service
│   │   ├── venv/                    # Python environment
│   │   ├── hls_output/              # HLS streams
│   │   └── logs/                    # Application logs
│
└── 📚 Documentation
    ├── PROJECT-DOCUMENTATION.md     # Complete overview
    ├── API-REFERENCE.md             # API docs
    ├── FRONTEND-GUIDE.md            # Frontend guide
    ├── BACKEND-GUIDE.md             # Backend guide
    ├── DEPLOYMENT-GUIDE.md          # Deployment guide
    ├── QUICK-START.md               # Quick start
    ├── SETUP.md                     # Setup guide
    └── HOW-TO-RUN.md                # Run instructions
```

---

## 🧪 Testing

**Backend:**
```bash
cd backend
bash test-backend-api.sh
```

**Frontend:**
```bash
npm test
```

---

## 🚀 Deployment

See **[DEPLOYMENT-GUIDE.md](docs/DEPLOYMENT-GUIDE.md)** for:
- Linux server deployment
- Docker deployment
- Cloud deployment (AWS, Azure)
- Security hardening
- Monitoring setup

---

## 📞 Support & Documentation

- **Full Documentation:** See `docs/` directory
- **API Reference:** [API-REFERENCE.md](docs/API-REFERENCE.md)
- **Issues:** Check troubleshooting in [PROJECT-DOCUMENTATION.md](docs/PROJECT-DOCUMENTATION.md)

---

## 📄 License

Proprietary - All rights reserved

---

## 🎉 Getting Started

1. **Read** [PROJECT-DOCUMENTATION.md](docs/PROJECT-DOCUMENTATION.md) for complete overview
2. **Setup** environment following [SETUP.md](docs/SETUP.md)
3. **Run** the project using [HOW-TO-RUN.md](docs/HOW-TO-RUN.md)
4. **Develop** with [FRONTEND-GUIDE.md](docs/FRONTEND-GUIDE.md) and [BACKEND-GUIDE.md](docs/BACKEND-GUIDE.md)
5. **Deploy** to production with [DEPLOYMENT-GUIDE.md](docs/DEPLOYMENT-GUIDE.md)

---

**Version:** 1.0.0  
**Last Updated:** January 12, 2026  
**Documentation:** Complete and up-to-date

## 🏗️ Project Structure

```
MobileApp/
├── src/
│   ├── screens/
│   │   ├── CameraConfigScreen.tsx    # Camera setup wizard (FR-A1)
│   │   └── StreamViewerScreen.tsx    # HLS video player (FR-C1-C4)
│   ├── components/
│   │   ├── NetworkScanner.tsx        # LAN device scanner (FR-A2)
│   │   └── AlarmModal.tsx            # Critical alarm UI (FR-Z1-Z2)
│   └── types/
│       └── index.ts                  # TypeScript interfaces
├── App.tsx                           # Main navigation setup
├── app.json                          # Expo configuration
├── package.json                      # Dependencies
└── tsconfig.json                     # TypeScript config
```

## 🔒 Security Features

### Secure Storage (NFR-A1)
All sensitive credentials (RTSP passwords, tunnel URLs) are stored using `expo-secure-store`, which provides:
- Hardware-backed encryption on iOS (Keychain)
- Encrypted SharedPreferences on Android
- No plain text storage

### Network Permissions
- **iOS**: `NSLocalNetworkUsageDescription` for LAN scanning
- **Android**: Internet, network state, WiFi state, vibration permissions

## 🎯 SRS Compliance

This application implements the complete Software Requirements Specification:

### Functional Requirements
- ✅ FR-A1: Configuration Dashboard with validation
- ✅ FR-A2: Network Discovery with LAN scanner
- ✅ FR-A3: Connection Test Logic
- ✅ FR-C1: Adaptive Video Player with HLS
- ✅ FR-C2: Stream State Management (Loading/Live/Error)
- ✅ FR-C3: Pull-to-Refresh stream reload
- ✅ FR-C4: Alert Snapshots carousel
- ✅ FR-Z1: Full-Screen Alarm Modal with visuals
- ✅ FR-Z2: Slide-to-Dismiss control

### Non-Functional Requirements
- ✅ NFR-A1: Secure credential storage
- ✅ NFR-A2: 10-second scan timeout
- ✅ NFR-A3: WiFi-only scanning guidance
- ✅ NFR-C1: Non-blocking UI during stream connection
- ✅ NFR-C2: Low-latency buffer configuration
- ✅ NFR-C3: Background audio stops on minimize

## 🧪 Testing

### Manual Testing
1. **Configuration Screen**
   - Enter invalid IP addresses (validation should prevent save)
   - Test with valid credentials
   - Use network scanner (requires WiFi)

2. **Stream Viewer**
   - Verify auto-play and muted state
   - Test pull-to-refresh functionality
   - Click alert snapshots for full view

3. **Alarm Modal**
   - Uncomment alarm trigger in StreamViewerScreen.tsx
   - Test slide-to-dismiss gesture
   - Verify vibration and visual effects

## 🚧 Production Considerations

### Replace Mock Data
- **HLS Stream URL**: Replace demo URL with your backend endpoint
- **Alert Snapshots**: Connect to real detection API
- **Network Scanner**: Implement native module for actual LAN scanning
- **Connection Test**: Use real ping/RTSP validation

### Backend Integration
```typescript
// Example: Fetch HLS URL from backend
const response = await fetch(`https://your-api.com/cameras/${cameraId}/stream`);
const { hlsUrl } = await response.json();
```

### Asset Preparation
Add these assets to `assets/` directory:
- `icon.png` (1024x1024)
- `splash.png` (1242x2436)
- `adaptive-icon.png` (Android, 1024x1024)
- `favicon.png` (Web, 32x32)

## 📱 Building for Production

### iOS
```bash
npx expo build:ios
```

### Android
```bash
npx expo build:android
```

## 🤝 Contributing

This project follows the SRS document specifications. Any modifications should:
1. Reference the specific FR/NFR requirement
2. Maintain TypeScript type safety
3. Follow React Native best practices
4. Test on both iOS and Android

## 📄 License

Proprietary - All rights reserved

## 📞 Support

For technical support or questions about implementation, contact the development team.

---

**Built with ❤️ using React Native & Expo**
