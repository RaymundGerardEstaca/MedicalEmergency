# API Reference Documentation
## CCTV Backend REST API

**Base URL:** `http://localhost:8000`  
**Version:** 4.0.0  
**Protocol:** HTTP/HTTPS + WebSocket  
**Authentication:** Bearer Token

---

## 📋 Table of Contents

1. [Authentication](#authentication)
2. [Device Management](#device-management)
3. [Streaming](#streaming)
4. [WiFi Configuration](#wifi-configuration)
5. [Health & Status](#health--status)
6. [WebSocket Endpoints](#websocket-endpoints)
7. [Error Handling](#error-handling)
8. [Rate Limiting](#rate-limiting)

---

## 🔐 Authentication

### Register User

**Endpoint:** `POST /api/auth/register`

**Description:** Create a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "name": "John Doe"
}
```

**Response:** `201 Created`
```json
{
  "user_id": "usr_abc123def456",
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2026-01-12T10:30:00.000Z"
}
```

**Error Responses:**
- `400 Bad Request` - Invalid email format or weak password
- `409 Conflict` - Email already registered

**Example:**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "name": "John Doe"
  }'
```

---

### Login

**Endpoint:** `POST /api/auth/login`

**Description:** Authenticate user and receive access token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response:** `200 OK`
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "user_id": "usr_abc123def456",
    "email": "user@example.com",
    "name": "John Doe"
  },
  "expires_at": "2026-01-13T10:30:00.000Z"
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid credentials
- `400 Bad Request` - Missing email or password

**Example:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

**Token Usage:**
Include token in subsequent requests:
```bash
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

### Logout

**Endpoint:** `POST /api/auth/logout`

**Description:** Invalidate current access token.

**Headers:**
```
Authorization: Bearer {token}
```

**Response:** `200 OK`
```json
{
  "message": "Successfully logged out"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/auth/logout \
  -H "Authorization: Bearer {your_token}"
```

---

### Get Current User

**Endpoint:** `GET /api/auth/me`

**Description:** Get information about the authenticated user.

**Headers:**
```
Authorization: Bearer {token}
```

**Response:** `200 OK`
```json
{
  "user_id": "usr_abc123def456",
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2026-01-10T08:00:00.000Z",
  "device_count": 5
}
```

---

## 📱 Device Management

### Register Device

**Endpoint:** `POST /api/devices/register`

**Description:** Register a new camera device.

**Headers:**
```
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "bleId": "ESP32_CAM_A1B2C3",
  "name": "Front Door Camera",
  "macAddress": "AA:BB:CC:DD:EE:FF",
  "wifiSSID": "HomeNetwork",
  "ipAddress": "192.168.1.100",
  "rtspUrl": "rtsp://admin:password@192.168.1.100:554/stream1"
}
```

**Response:** `201 Created`
```json
{
  "device_id": "dev_xyz789abc012",
  "bleId": "ESP32_CAM_A1B2C3",
  "name": "Front Door Camera",
  "macAddress": "AA:BB:CC:DD:EE:FF",
  "wifiSSID": "HomeNetwork",
  "ipAddress": "192.168.1.100",
  "rtspUrl": "rtsp://admin:****@192.168.1.100:554/stream1",
  "isOnline": false,
  "created_at": "2026-01-12T10:30:00.000Z",
  "owner_id": "usr_abc123def456"
}
```

**Error Responses:**
- `400 Bad Request` - Invalid device data
- `409 Conflict` - Device already registered

**Example:**
```bash
curl -X POST http://localhost:8000/api/devices/register \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "bleId": "ESP32_CAM_A1B2C3",
    "name": "Front Door Camera",
    "ipAddress": "192.168.1.100",
    "rtspUrl": "rtsp://admin:password@192.168.1.100:554/stream1"
  }'
```

---

### List All Devices

**Endpoint:** `GET /api/devices`

**Description:** Get all devices for the authenticated user.

**Headers:**
```
Authorization: Bearer {token}
```

**Response:** `200 OK`
```json
{
  "devices": [
    {
      "device_id": "dev_xyz789abc012",
      "name": "Front Door Camera",
      "ipAddress": "192.168.1.100",
      "isOnline": true,
      "lastSeen": "2026-01-12T10:28:00.000Z",
      "streamUrl": "rtsp://admin:****@192.168.1.100:554/stream1"
    },
    {
      "device_id": "dev_aaa111bbb222",
      "name": "Backyard Camera",
      "ipAddress": "192.168.1.101",
      "isOnline": false,
      "lastSeen": "2026-01-12T09:45:00.000Z",
      "streamUrl": "rtsp://admin:****@192.168.1.101:554/stream1"
    }
  ],
  "total": 2
}
```

**Example:**
```bash
curl -X GET http://localhost:8000/api/devices \
  -H "Authorization: Bearer {token}"
```

---

### Get Device Details

**Endpoint:** `GET /api/devices/{device_id}`

**Description:** Get detailed information about a specific device.

**Path Parameters:**
- `device_id` (string) - Device identifier

**Headers:**
```
Authorization: Bearer {token}
```

**Response:** `200 OK`
```json
{
  "device_id": "dev_xyz789abc012",
  "bleId": "ESP32_CAM_A1B2C3",
  "name": "Front Door Camera",
  "macAddress": "AA:BB:CC:DD:EE:FF",
  "wifiSSID": "HomeNetwork",
  "ipAddress": "192.168.1.100",
  "rtspUrl": "rtsp://admin:****@192.168.1.100:554/stream1",
  "isOnline": true,
  "lastSeen": "2026-01-12T10:28:00.000Z",
  "created_at": "2026-01-10T08:00:00.000Z",
  "owner_id": "usr_abc123def456",
  "firmware_version": "1.2.3",
  "uptime_seconds": 86400
}
```

**Error Responses:**
- `404 Not Found` - Device not found
- `403 Forbidden` - Not authorized to access this device

---

### Update Device

**Endpoint:** `PUT /api/devices/{device_id}`

**Description:** Update device configuration.

**Path Parameters:**
- `device_id` (string) - Device identifier

**Headers:**
```
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "name": "Updated Camera Name",
  "ipAddress": "192.168.1.105",
  "rtspUrl": "rtsp://admin:newpass@192.168.1.105:554/stream1",
  "isOnline": true
}
```

**Response:** `200 OK`
```json
{
  "device_id": "dev_xyz789abc012",
  "name": "Updated Camera Name",
  "ipAddress": "192.168.1.105",
  "rtspUrl": "rtsp://admin:****@192.168.1.105:554/stream1",
  "isOnline": true,
  "updated_at": "2026-01-12T10:30:00.000Z"
}
```

**Example:**
```bash
curl -X PUT http://localhost:8000/api/devices/dev_xyz789abc012 \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Camera Name",
    "ipAddress": "192.168.1.105"
  }'
```

---

### Delete Device

**Endpoint:** `DELETE /api/devices/{device_id}`

**Description:** Remove a device from the system.

**Path Parameters:**
- `device_id` (string) - Device identifier

**Headers:**
```
Authorization: Bearer {token}
```

**Response:** `200 OK`
```json
{
  "message": "Device deleted successfully",
  "device_id": "dev_xyz789abc012"
}
```

**Error Responses:**
- `404 Not Found` - Device not found
- `403 Forbidden` - Not authorized to delete this device

---

### Device Heartbeat

**Endpoint:** `POST /api/devices/{device_id}/heartbeat`

**Description:** Update device's last seen timestamp.

**Path Parameters:**
- `device_id` (string) - Device identifier

**Headers:**
```
Authorization: Bearer {token}
```

**Response:** `200 OK`
```json
{
  "device_id": "dev_xyz789abc012",
  "isOnline": true,
  "lastSeen": "2026-01-12T10:30:00.000Z",
  "uptime_seconds": 3600
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/devices/dev_xyz789abc012/heartbeat \
  -H "Authorization: Bearer {token}"
```

---

### Get Device Stream

**Endpoint:** `GET /api/devices/{device_id}/stream`

**Description:** Get streaming information for a device.

**Path Parameters:**
- `device_id` (string) - Device identifier

**Headers:**
```
Authorization: Bearer {token}
```

**Response:** `200 OK`
```json
{
  "device_id": "dev_xyz789abc012",
  "stream_id": "strm_abc123def456",
  "hls_url": "http://192.168.1.200:8000/hls/strm_abc123def456/stream.m3u8",
  "websocket_url": "ws://192.168.1.200:8000/ws/stream/strm_abc123def456",
  "rtsp_url": "rtsp://admin:****@192.168.1.100:554/stream1",
  "status": "streaming",
  "started_at": "2026-01-12T10:25:00.000Z"
}
```

---

## 📹 Streaming

### Start Stream

**Endpoint:** `POST /api/stream/start`

**Description:** Start RTSP to HLS transcoding for a camera.

**Headers:**
```
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "url": "rtsp://admin:password@192.168.1.100:554/stream1",
  "stream_id": "custom_stream_id",
  "mode": "both"
}
```

**Parameters:**
- `url` (string, required) - RTSP stream URL
- `stream_id` (string, optional) - Custom stream identifier (auto-generated if not provided)
- `mode` (string, optional) - Streaming mode: `hls`, `websocket`, or `both` (default: `both`)

**Response:** `200 OK`
```json
{
  "stream_id": "strm_abc123def456",
  "status": "started",
  "mode": "both",
  "hls_url": "http://192.168.1.200:8000/hls/strm_abc123def456/stream.m3u8",
  "websocket_url": "ws://192.168.1.200:8000/ws/stream/strm_abc123def456",
  "started_at": "2026-01-12T10:30:00.000Z",
  "estimated_ready_in_seconds": 4
}
```

**Error Responses:**
- `400 Bad Request` - Invalid RTSP URL
- `409 Conflict` - Stream already active
- `500 Internal Server Error` - FFmpeg not available

**Example:**
```bash
curl -X POST http://localhost:8000/api/stream/start \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "rtsp://admin:password@192.168.1.100:554/stream1",
    "mode": "both"
  }'
```

---

### Stop Stream

**Endpoint:** `POST /api/stream/stop`

**Description:** Stop an active stream.

**Headers:**
```
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "stream_id": "strm_abc123def456"
}
```

**Response:** `200 OK`
```json
{
  "message": "Stream stopped successfully",
  "stream_id": "strm_abc123def456",
  "stopped_at": "2026-01-12T10:35:00.000Z",
  "total_duration_seconds": 300
}
```

**Error Responses:**
- `404 Not Found` - Stream not found

---

### Get All Stream Statuses

**Endpoint:** `GET /api/stream/status`

**Description:** Get status of all active streams.

**Headers:**
```
Authorization: Bearer {token}
```

**Response:** `200 OK`
```json
{
  "streams": [
    {
      "stream_id": "strm_abc123def456",
      "status": "streaming",
      "mode": "both",
      "health": "healthy",
      "started_at": "2026-01-12T10:25:00.000Z",
      "uptime_seconds": 300,
      "url": "rtsp://admin:****@192.168.1.100:554/stream1",
      "hls_url": "http://192.168.1.200:8000/hls/strm_abc123def456/stream.m3u8",
      "websocket_url": "ws://192.168.1.200:8000/ws/stream/strm_abc123def456",
      "restart_attempts": 0,
      "fps": 30,
      "resolution": "1920x1080"
    }
  ],
  "total_active": 1
}
```

---

### Get Stream Status

**Endpoint:** `GET /api/stream/{stream_id}/status`

**Description:** Get status of a specific stream.

**Path Parameters:**
- `stream_id` (string) - Stream identifier

**Headers:**
```
Authorization: Bearer {token}
```

**Response:** `200 OK`
```json
{
  "stream_id": "strm_abc123def456",
  "status": "streaming",
  "mode": "both",
  "health": "healthy",
  "started_at": "2026-01-12T10:25:00.000Z",
  "uptime_seconds": 300,
  "url": "rtsp://admin:****@192.168.1.100:554/stream1",
  "hls_url": "http://192.168.1.200:8000/hls/strm_abc123def456/stream.m3u8",
  "websocket_url": "ws://192.168.1.200:8000/ws/stream/strm_abc123def456",
  "restart_attempts": 0,
  "last_frame_at": "2026-01-12T10:30:15.000Z",
  "ffmpeg": {
    "pid": 12345,
    "cpu_percent": 15.2,
    "memory_mb": 128.5,
    "command": "ffmpeg -rtsp_transport tcp -i rtsp://..."
  },
  "hls": {
    "playlist_path": "/backend/hls_output/strm_abc123def456/stream.m3u8",
    "segment_count": 3,
    "total_size_mb": 12.5
  },
  "stream_info": {
    "fps": 30,
    "resolution": "1920x1080",
    "codec": "h264",
    "bitrate_kbps": 2048
  }
}
```

**Error Responses:**
- `404 Not Found` - Stream not found

---

### Probe RTSP Stream

**Endpoint:** `POST /api/stream/probe`

**Description:** Validate RTSP connection and get stream information.

**Headers:**
```
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "url": "rtsp://admin:password@192.168.1.100:554/stream1"
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "url": "rtsp://admin:****@192.168.1.100:554/stream1",
  "resolution": "1920x1080",
  "fps": 30.0,
  "codec": "h264",
  "bitrate_kbps": 2048,
  "thumbnail": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
}
```

**Error Response:** `200 OK` (with success: false)
```json
{
  "success": false,
  "error": "Connection timeout",
  "url": "rtsp://admin:****@192.168.1.100:554/stream1"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/stream/probe \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "rtsp://admin:password@192.168.1.100:554/stream1"
  }'
```

---

### Check Stream Connectivity

**Endpoint:** `POST /api/stream/check-connectivity`

**Description:** Quick connectivity test for RTSP stream.

**Headers:**
```
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "url": "rtsp://admin:password@192.168.1.100:554/stream1"
}
```

**Response:** `200 OK`
```json
{
  "reachable": true,
  "latency_ms": 45,
  "url": "rtsp://admin:****@192.168.1.100:554/stream1"
}
```

---

### Discover Streams

**Endpoint:** `POST /api/stream/discover`

**Description:** Discover RTSP streams on the local network.

**Headers:**
```
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "subnet": "192.168.1.0/24",
  "ports": [554, 8554],
  "timeout_seconds": 2
}
```

**Response:** `200 OK`
```json
{
  "discovered": [
    {
      "ip": "192.168.1.100",
      "port": 554,
      "manufacturer": "Hikvision",
      "model": "DS-2CD2142FWD-I",
      "rtsp_paths": [
        "/stream1",
        "/Streaming/Channels/101"
      ]
    },
    {
      "ip": "192.168.1.101",
      "port": 554,
      "manufacturer": "Dahua",
      "rtsp_paths": ["/cam/realmonitor?channel=1&subtype=0"]
    }
  ],
  "total_found": 2,
  "scan_duration_seconds": 15.3
}
```

---

## 📡 WiFi Configuration

### Validate WiFi Credentials

**Endpoint:** `POST /api/wifi/validate`

**Description:** Validate WiFi network SSID format.

**Headers:**
```
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "ssid": "HomeNetwork"
}
```

**Response:** `200 OK`
```json
{
  "valid": true,
  "ssid": "HomeNetwork",
  "length": 11,
  "has_special_chars": false
}
```

**Error Response:**
```json
{
  "valid": false,
  "ssid": "Invalid@SSID!!!!",
  "error": "SSID contains invalid characters"
}
```

---

## 🏥 Health & Status

### Root Endpoint

**Endpoint:** `GET /`

**Description:** Basic status check.

**Response:** `200 OK`
```json
{
  "service": "CCTV Unified Backend",
  "status": "operational",
  "version": "4.0.0",
  "timestamp": "2026-01-12T10:30:00.000Z"
}
```

---

### Health Check

**Endpoint:** `GET /api/health`

**Description:** Comprehensive health check.

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "timestamp": "2026-01-12T10:30:00.000Z",
  "version": "4.0.0",
  "uptime_seconds": 3600,
  "components": {
    "ffmpeg": {
      "available": true,
      "version": "8.0.1",
      "path": "/usr/bin/ffmpeg"
    },
    "storage": {
      "hls_output_dir": "/backend/hls_output",
      "disk_space_gb": 256.5,
      "disk_used_gb": 12.3
    },
    "database": {
      "devices": 10,
      "users": 3
    },
    "streaming": {
      "active_streams": 2,
      "total_streams_today": 15
    }
  }
}
```

---

### Demo Page

**Endpoint:** `GET /demo`

**Description:** Interactive HTML demo page for testing streams.

**Response:** HTML page with:
- Stream start/stop controls
- RTSP URL input
- Live video preview
- WebSocket connection status
- Stream information display
- Console logs

---

## 🔌 WebSocket Endpoints

### WebSocket Stream

**Endpoint:** `WS /ws/stream/{stream_id}`

**Description:** Real-time JPEG frame streaming via WebSocket.

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/stream/strm_abc123def456');

ws.onopen = () => {
  console.log('Connected to stream');
};

ws.onmessage = (event) => {
  // Receive JPEG frame as Blob
  const blob = event.data;
  const url = URL.createObjectURL(blob);
  imageElement.src = url;
};

ws.onclose = () => {
  console.log('Disconnected from stream');
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};
```

**Frame Format:**
- Binary JPEG data
- ~30 FPS
- Resolution: Same as source stream
- Quality: 85% JPEG compression

**Auto-Reconnect:**
Client should implement reconnection logic:
```javascript
function connectStream(streamId) {
  const ws = new WebSocket(`ws://localhost:8000/ws/stream/${streamId}`);
  
  ws.onclose = () => {
    setTimeout(() => connectStream(streamId), 5000); // Retry in 5s
  };
  
  return ws;
}
```

---

## ❌ Error Handling

### Error Response Format

All errors follow this structure:

```json
{
  "detail": "Human-readable error message",
  "error_code": "ERROR_TYPE",
  "timestamp": "2026-01-12T10:30:00.000Z",
  "path": "/api/stream/start",
  "request_id": "req_abc123"
}
```

### HTTP Status Codes

| Code | Meaning | Common Causes |
|------|---------|---------------|
| `200` | OK | Request successful |
| `201` | Created | Resource created successfully |
| `400` | Bad Request | Invalid input, validation error |
| `401` | Unauthorized | Missing or invalid auth token |
| `403` | Forbidden | Insufficient permissions |
| `404` | Not Found | Resource doesn't exist |
| `409` | Conflict | Resource already exists |
| `429` | Too Many Requests | Rate limit exceeded |
| `500` | Internal Server Error | Server-side error |
| `502` | Bad Gateway | Upstream service error |
| `503` | Service Unavailable | Service temporarily down |

### Common Error Codes

```json
// Authentication Errors
{
  "detail": "Invalid credentials",
  "error_code": "AUTH_INVALID_CREDENTIALS"
}

// Validation Errors
{
  "detail": "Invalid RTSP URL format",
  "error_code": "VALIDATION_INVALID_URL"
}

// Resource Errors
{
  "detail": "Device not found",
  "error_code": "RESOURCE_NOT_FOUND"
}

// Streaming Errors
{
  "detail": "FFmpeg process failed",
  "error_code": "STREAM_FFMPEG_ERROR"
}

// Network Errors
{
  "detail": "Connection timeout",
  "error_code": "NETWORK_TIMEOUT"
}
```

---

## ⏱️ Rate Limiting

**Current Limits:**
- Authentication: 10 requests/minute
- Device Operations: 100 requests/minute
- Stream Start: 5 requests/minute per device
- General API: 1000 requests/minute

**Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 85
X-RateLimit-Reset: 1736676600
```

**Rate Limit Exceeded:**
```json
{
  "detail": "Rate limit exceeded. Try again in 45 seconds.",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "retry_after": 45
}
```

---

## 📊 HLS Streaming

### HLS Playlist URL

**Format:** `GET /hls/{stream_id}/stream.m3u8`

**Example:**
```
http://localhost:8000/hls/strm_abc123def456/stream.m3u8
```

**Playlist Content:**
```m3u8
#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:2
#EXT-X-MEDIA-SEQUENCE:12

#EXTINF:2.000000,
segment_012.ts
#EXTINF:2.000000,
segment_013.ts
#EXTINF:2.000000,
segment_014.ts
```

**Segment URLs:**
```
http://localhost:8000/hls/strm_abc123def456/segment_012.ts
http://localhost:8000/hls/strm_abc123def456/segment_013.ts
```

### HLS Configuration

- **Segment Duration:** 2 seconds (low latency)
- **Playlist Size:** 3 segments
- **Total Buffer:** ~6 seconds
- **Codec:** H.264 (video) + AAC (audio)
- **Resolution:** Original or downscaled
- **Bitrate:** Adaptive based on source

---

## 🧪 Testing the API

### Using cURL

```bash
# 1. Register user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!","name":"Test User"}'

# 2. Login
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}' \
  | jq -r '.token')

# 3. Register device
curl -X POST http://localhost:8000/api/devices/register \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "bleId":"ESP32_CAM_TEST",
    "name":"Test Camera",
    "ipAddress":"192.168.1.100",
    "rtspUrl":"rtsp://admin:pass@192.168.1.100:554/stream1"
  }'

# 4. Start stream
curl -X POST http://localhost:8000/api/stream/start \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url":"rtsp://admin:pass@192.168.1.100:554/stream1",
    "mode":"both"
  }'

# 5. Check stream status
curl -X GET http://localhost:8000/api/stream/status \
  -H "Authorization: Bearer $TOKEN"
```

### Using Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Login
response = requests.post(f"{BASE_URL}/api/auth/login", json={
    "email": "test@example.com",
    "password": "Test123!"
})
token = response.json()["token"]

# Headers with auth
headers = {"Authorization": f"Bearer {token}"}

# Start stream
response = requests.post(
    f"{BASE_URL}/api/stream/start",
    headers=headers,
    json={
        "url": "rtsp://admin:pass@192.168.1.100:554/stream1",
        "mode": "both"
    }
)

stream_data = response.json()
print(f"Stream started: {stream_data['hls_url']}")
```

### Using Postman

**Collection:** Import the provided Postman collection:
```json
{
  "info": {
    "name": "CCTV Backend API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "auth": {
    "type": "bearer",
    "bearer": [{"key": "token", "value": "{{auth_token}}"}]
  }
}
```

---

## 📝 Notes

- All timestamps are in ISO 8601 format (UTC)
- Passwords are hashed with SHA256 before storage
- RTSP credentials are masked in logs and responses
- WebSocket connections auto-close after 5 minutes of inactivity
- HLS segments are automatically deleted after 30 seconds

---

**Last Updated:** January 12, 2026  
**API Version:** 4.0.0  
**Documentation Version:** 1.0.0
