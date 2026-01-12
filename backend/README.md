# CCTV BLE Provisioning System - Python Backend

## Overview
This is a Flask-based REST API backend for managing CCTV devices that are provisioned via Bluetooth Low Energy (BLE) from the React Native mobile app.

## Features
- ✅ Device registration after BLE provisioning
- ✅ Device management (CRUD operations)
- ✅ Device heartbeat monitoring
- ✅ WiFi network validation (2.4 GHz check)
- ✅ Firmware update checking
- ✅ Stream URL management
- ✅ Persistent storage (JSON files)

## Installation

### 1. Create Virtual Environment
```bash
cd backend
python -m venv venv
```

### 2. Activate Virtual Environment
**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## Running the Server

```bash
python app.py
```

The server will start on `http://0.0.0.0:5000`

## API Endpoints

### Device Management

#### Register Device
```http
POST /api/devices/register
Content-Type: application/json

{
  "bleId": "device-uuid",
  "name": "Front Door Camera",
  "macAddress": "AA:BB:CC:DD:EE:FF",
  "wifiSSID": "MyNetwork",
  "ipAddress": "192.168.1.100",
  "userId": "user123"
}
```

#### Get All Devices
```http
GET /api/devices?userId=user123
```

#### Get Device Details
```http
GET /api/devices/{device_id}
```

#### Update Device
```http
PUT /api/devices/{device_id}
Content-Type: application/json

{
  "name": "New Camera Name",
  "ipAddress": "192.168.1.101",
  "isOnline": true
}
```

#### Delete Device
```http
DELETE /api/devices/{device_id}
```

### Device Status

#### Send Heartbeat
```http
POST /api/devices/{device_id}/heartbeat
Content-Type: application/json

{
  "ipAddress": "192.168.1.100"
}
```

### WiFi Validation

#### Validate WiFi Network
```http
POST /api/wifi/validate
Content-Type: application/json

{
  "ssid": "MyNetwork-5G"
}
```

### Firmware

#### Check Firmware Update
```http
GET /api/devices/{device_id}/firmware
```

### Stream Management

#### Get Stream URL
```http
GET /api/devices/{device_id}/stream
```

### Health Check

#### Check API Health
```http
GET /api/health
```

## Data Storage

The backend uses JSON files for data persistence:
- `devices_db.json` - Stores all registered devices
- `users_db.json` - Stores user information

For production, migrate to PostgreSQL or MongoDB.

## Security Considerations

⚠️ **Important**: This is a development version. For production:

1. Add authentication (JWT tokens)
2. Add HTTPS/TLS encryption
3. Implement rate limiting
4. Add input validation and sanitization
5. Use a proper database (PostgreSQL/MongoDB)
6. Add device authentication tokens
7. Encrypt sensitive data

## Integration with React Native App

The mobile app communicates with this backend after BLE provisioning:

1. **BLE Provisioning** → Device connects to WiFi
2. **Device Registration** → App calls `/api/devices/register`
3. **Heartbeat** → Device periodically sends status updates
4. **Stream Access** → App fetches stream URLs from backend

## Environment Variables

Create a `.env` file:

```env
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:pass@localhost/cctv_db
```

## Testing

Use curl or Postman to test endpoints:

```bash
# Register a device
curl -X POST http://localhost:5000/api/devices/register \
  -H "Content-Type: application/json" \
  -d '{
    "bleId": "test-device-001",
    "name": "Test Camera",
    "macAddress": "AA:BB:CC:DD:EE:FF",
    "wifiSSID": "TestNetwork",
    "ipAddress": "192.168.1.100"
  }'

# Get all devices
curl http://localhost:5000/api/devices

# Health check
curl http://localhost:5000/api/health
```

## Architecture

```
Mobile App (React Native)
    ↓ BLE Provisioning
CCTV Device
    ↓ WiFi Connection
Router/Network
    ↓ Internet
Flask Backend API
    ↓ Storage
devices_db.json
```

## License

MIT License - For Thesis Research Project
