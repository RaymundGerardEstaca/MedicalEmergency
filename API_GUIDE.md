# Frontend API Integration Guide

## What I Created

I've set up **Frontend API** functions that your React app uses to communicate with a backend CCTV server. Here's how it works:

---

## 1. API Service File (`src/services/api.js`)

This file contains all the functions your app needs to talk to the backend:

### Authentication Functions
```javascript
authAPI.login(email, password)          // Send login credentials
authAPI.signup(email, password, name)   // Create new account
authAPI.googleSignIn(googleToken)       // Google OAuth login
authAPI.logout()                        // Clear login session
```

### Camera Functions
```javascript
cameraAPI.getCameras()                  // Get all user's cameras
cameraAPI.addCamera(cameraData)        // Add new camera
cameraAPI.deleteCamera(cameraId)       // Remove a camera
cameraAPI.getCameraStream(cameraId)    // Get camera video stream
```

### Device Discovery Functions
```javascript
discoveryAPI.scanDevices(mode)         // Scan for devices (bluetooth/wifi)
discoveryAPI.pairDevice(deviceId, mode) // Pair with discovered device
discoveryAPI.stopScan()                // Stop scanning
```

### Statistics Functions
```javascript
statsAPI.getStats()                    // Get dashboard stats
```

---

## 2. How Your App Uses These APIs

### In App.jsx (Login Page)
```javascript
const handleSignIn = async (e) => {
  e.preventDefault();
  try {
    // Calls your backend login endpoint
    const result = await authAPI.login(email, password);
    setIsLoggedIn(true);
  } catch (err) {
    setError(err.message); // Show error if login fails
  }
};
```

### In Dashboard.jsx
```javascript
useEffect(() => {
  // Fetch cameras and stats when page loads
  const camerasData = await cameraAPI.getCameras();
  const statsData = await statsAPI.getStats();
}, []);
```

### In DiscoverCameras.jsx
```javascript
const handleScan = async () => {
  // Scan for devices to pair
  const devices = await discoveryAPI.scanDevices(scanMode);
};
```

---

## 3. Backend Endpoints You Need to Create

Your backend server needs to provide these endpoints:

### Authentication Endpoints
```
POST /api/auth/login
  Request: { email, password }
  Response: { token, user: { id, email, name } }

POST /api/auth/signup
  Request: { email, password, name }
  Response: { token, user: { id, email, name } }

POST /api/auth/google
  Request: { token }
  Response: { token, user: { id, email, name } }
```

### Camera Endpoints
```
GET /api/cameras
  Response: [{ id, name, status, location, ... }]

POST /api/cameras
  Request: { name, deviceId, location }
  Response: { id, name, status, ... }

DELETE /api/cameras/:cameraId
  Response: { success: true }

GET /api/cameras/:cameraId/stream
  Response: { streamUrl, ... }
```

### Device Discovery Endpoints
```
POST /api/devices/scan
  Request: { mode } // "bluetooth" or "wifi"
  Response: [{ id, name, signal, ... }]

POST /api/devices/pair
  Request: { deviceId, mode }
  Response: { id, name, paired: true }

POST /api/devices/scan/stop
  Response: { success: true }
```

### Statistics Endpoint
```
GET /api/stats
  Response: { totalCameras: 5, online: 3, offline: 2, alerts: 12 }
```

---

## 4. Authentication Token (JWT)

Your API uses a token-based system:

1. User logs in → Backend sends back a **token**
2. Token is saved in `localStorage` 
3. Every API call includes this token in the header:
   ```javascript
   headers: {
     'Authorization': `Bearer ${token}`
   }
   ```
4. Backend validates the token to know who the user is

---

## 5. Backend Server Setup (Example)

You'll need to create a backend server (Node.js, Python, Java, etc.) that:
1. Listens on `http://localhost:3001` (or whatever port you choose)
2. Implements all the endpoints above
3. Connects to your CCTV hardware
4. Returns JSON responses

**Change the API_BASE_URL if your backend runs on a different server:**
```javascript
// In api.js
const API_BASE_URL = 'http://your-backend-server:3001/api';
```

---

## 6. Error Handling

All API functions have built-in error handling:
```javascript
try {
  const result = await cameraAPI.getCameras();
} catch (error) {
  console.error("Failed to get cameras:", error);
  // Show error to user
}
```

---

## 7. Current Status

✅ **Frontend is ready!** Your React app can now:
- Make API calls to a backend
- Handle loading states
- Display errors
- Store authentication tokens
- Send data to the server

❌ **Backend still needed** - You need to create the actual server that:
- Receives these API calls
- Connects to CCTV devices
- Stores data in a database
- Returns proper responses

---

## Next Steps

1. **Create a backend server** (Node.js + Express recommended for beginners)
2. **Implement all the endpoints** shown above
3. **Connect to CCTV hardware** (this depends on your CCTV system)
4. **Test by running your React app** and trying to login

Would you like help setting up a simple Node.js backend?
