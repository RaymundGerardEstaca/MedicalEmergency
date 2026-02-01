// Mock API Service
// Simulates backend responses for testing without a real server

const MOCK_DELAY = 800; // Simulate network delay

const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

export const mockAuthAPI = {
  login: async (email, password) => {
    await delay(MOCK_DELAY);
    
    if (!email || !password) {
      throw new Error("Email and password required");
    }
    
    // Simulate successful login
    return {
      token: "mock_jwt_token_" + Date.now(),
      user: {
        id: "user_123",
        email: email,
        name: email.split("@")[0]
      }
    };
  },

  signup: async (email, password, name) => {
    await delay(MOCK_DELAY);
    
    if (!email || !password || !name) {
      throw new Error("All fields required");
    }
    
    if (password.length < 6) {
      throw new Error("Password must be at least 6 characters");
    }
    
    // Simulate successful signup
    return {
      token: "mock_jwt_token_" + Date.now(),
      user: {
        id: "user_" + Math.random().toString(36).substr(2, 9),
        email: email,
        name: name
      }
    };
  },

  googleSignIn: async (googleToken) => {
    await delay(MOCK_DELAY);
    
    // Simulate Google login
    return {
      token: "mock_google_jwt_" + Date.now(),
      user: {
        id: "user_google_123",
        email: "user@gmail.com",
        name: "Google User"
      }
    };
  },

  logout: () => {
    localStorage.removeItem("authToken");
  }
};

export const mockCameraAPI = {
  getCameras: async () => {
    await delay(MOCK_DELAY);
    
    // Return empty array (no cameras yet)
    // In a real app, this would return user's cameras
    return [];
  },

  addCamera: async (cameraData) => {
    await delay(MOCK_DELAY);
    
    return {
      id: "camera_" + Math.random().toString(36).substr(2, 9),
      name: cameraData.name,
      status: "online",
      location: cameraData.location || "Living Room"
    };
  },

  deleteCamera: async (cameraId) => {
    await delay(MOCK_DELAY);
    
    return { success: true, message: "Camera deleted" };
  },

  getCameraStream: async (cameraId) => {
    await delay(MOCK_DELAY);
    
    return {
      streamUrl: "rtsp://example.com/stream",
      status: "active"
    };
  }
};

export const mockDiscoveryAPI = {
  scanDevices: async (mode) => {
    await delay(2000); // Longer delay to simulate actual scanning
    
    // Simulate finding some devices based on mode
    const devices = mode === "bluetooth" 
      ? [
          { id: "device_bt_1", name: "Camera 1", signal: "Strong (-45dBm)" },
          { id: "device_bt_2", name: "Camera 2", signal: "Medium (-65dBm)" }
        ]
      : [
          { id: "device_wifi_1", name: "SmartCam-5G", signal: "5GHz Network" },
          { id: "device_wifi_2", name: "SmartCam-2G", signal: "2.4GHz Network" }
        ];
    
    // Sometimes return empty to test "no devices" state
    return Math.random() > 0.5 ? devices : [];
  },

  pairDevice: async (deviceId, mode) => {
    await delay(MOCK_DELAY);
    
    return {
      success: true,
      deviceId: deviceId,
      message: "Device paired successfully",
      cameraInfo: {
        id: "camera_" + Math.random().toString(36).substr(2, 9),
        name: "Paired Camera",
        status: "online"
      }
    };
  },

  stopScan: async () => {
    await delay(500);
    
    return { success: true };
  }
};

export const mockStatsAPI = {
  getStats: async () => {
    await delay(MOCK_DELAY);
    
    // Return mock dashboard statistics
    return {
      totalCameras: 3,
      online: 2,
      offline: 1,
      alerts: 5
    };
  }
};
