// Frontend API Service
// This file handles all communication between your React app and the backend server

// Use mock API in development, real API in production
import { mockApi } from './mockApi';

// Aliasing mockApi to avoid TypeScript errors for undefined objects
const mockAuthAPI: any = mockApi;
const mockCameraAPI: any = mockApi;
const mockDiscoveryAPI: any = mockApi;
const mockStatsAPI: any = mockApi;

// Toggle between mock and real API
const USE_MOCK_API = false; // Set to false to use real backend

const API_BASE_URL = 'http://localhost:3001/api';

// ============================================
// AUTHENTICATION API
// ============================================

export const authAPI = {
  // Login with email and password
  login: async (email: any, password: any) => {
    try {
      if (USE_MOCK_API) {
        return await mockApi.login(email, password);
      }
      
      const response = await fetch(`${API_BASE_URL}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password })
      });
      
      if (!response.ok) {
        throw new Error('Login failed');
      }
      
      const data = await response.json();
      localStorage.setItem('authToken', data.token);
      return data;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  },

  // Sign up new user
  signup: async (email: any, password: any, name: any) => {
    try {
      if (USE_MOCK_API) {
        return await mockApi.signup(email, password, name);
      }
      
      const response = await fetch(`${API_BASE_URL}/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password, name })
      });
      
      if (!response.ok) {
        throw new Error('Sign up failed');
      }
      
      const data = await response.json();
      localStorage.setItem('authToken', data.token);
      return data;
    } catch (error) {
      console.error('Sign up error:', error);
      throw error;
    }
  },

  // Logout - clear stored token
  logout: () => {
    if (USE_MOCK_API) {
      mockAuthAPI.logout();
    } else {
      localStorage.removeItem('authToken');
    }
  },

  // Google OAuth login
  googleSignIn: async (googleToken: any) => {
    try {
      if (USE_MOCK_API) {
        return await mockAuthAPI.googleSignIn(googleToken);
      }
      
      const response = await fetch(`${API_BASE_URL}/auth/google`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token: googleToken })
      });
      
      if (!response.ok) {
        throw new Error('Google sign in failed');
      }
      
      const data = await response.json();
      localStorage.setItem('authToken', data.token);
      return data;
    } catch (error) {
      console.error('Google sign in error:', error);
      throw error;
    }
  }
};

// ============================================
// CAMERA API
// ============================================

export const cameraAPI = {
  // Get all cameras for logged in user
  getCameras: async () => {
    try {
      if (USE_MOCK_API) {
        return await mockCameraAPI.getCameras();
      }
      
      const token = localStorage.getItem('authToken');
      const response = await fetch(`${API_BASE_URL}/cameras`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch cameras');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Get cameras error:', error);
      throw error;
    }
  },

  // Add a new camera
  addCamera: async (cameraData: any) => {
    try {
      if (USE_MOCK_API) {
        return await mockCameraAPI.addCamera(cameraData);
      }
      
      const token = localStorage.getItem('authToken');
      const response = await fetch(`${API_BASE_URL}/cameras`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(cameraData)
      });
      
      if (!response.ok) {
        throw new Error('Failed to add camera');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Add camera error:', error);
      throw error;
    }
  },

  // Delete a camera
  deleteCamera: async (cameraId: any) => {
    try {
      if (USE_MOCK_API) {
        return await mockCameraAPI.deleteCamera(cameraId);
      }
      
      const token = localStorage.getItem('authToken');
      const response = await fetch(`${API_BASE_URL}/cameras/${cameraId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to delete camera');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Delete camera error:', error);
      throw error;
    }
  },

  // Get camera details/stream
  getCameraStream: async (cameraId: any) => {
    try {
      if (USE_MOCK_API) {
        return await mockCameraAPI.getCameraStream(cameraId);
      }
      
      const token = localStorage.getItem('authToken');
      const response = await fetch(`${API_BASE_URL}/cameras/${cameraId}/stream`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to get camera stream');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Get camera stream error:', error);
      throw error;
    }
  }
};

// ============================================
// DEVICE DISCOVERY API
// ============================================

export const discoveryAPI = {
  // Scan for available devices (Bluetooth or WiFi)
  scanDevices: async (mode: any) => {
    try {
      if (USE_MOCK_API) {
        return await mockDiscoveryAPI.scanDevices(mode);
      }
      
      const token = localStorage.getItem('authToken');
      const response = await fetch(`${API_BASE_URL}/devices/scan`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ mode })
      });
      
      if (!response.ok) {
        throw new Error('Scan failed');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Scan error:', error);
      throw error;
    }
  },

  // Pair with a discovered device
  pairDevice: async (deviceId: any, mode: any) => {
    try {
      if (USE_MOCK_API) {
        return await mockDiscoveryAPI.pairDevice(deviceId, mode);
      }
      
      const token = localStorage.getItem('authToken');
      const response = await fetch(`${API_BASE_URL}/devices/pair`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ deviceId, mode })
      });
      
      if (!response.ok) {
        throw new Error('Pairing failed');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Pairing error:', error);
      throw error;
    }
  },

  // Stop scanning
  stopScan: async () => {
    try {
      if (USE_MOCK_API) {
        return await mockDiscoveryAPI.stopScan();
      }
      
      const token = localStorage.getItem('authToken');
      const response = await fetch(`${API_BASE_URL}/devices/scan/stop`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to stop scan');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Stop scan error:', error);
      throw error;
    }
  }
};

// ============================================
// STATISTICS API
// ============================================

export const statsAPI = {
  // Get dashboard statistics
  getStats: async () => {
    try {
      if (USE_MOCK_API) {
        return await mockStatsAPI.getStats();
      }
      
      const token = localStorage.getItem('authToken');
      const response = await fetch(`${API_BASE_URL}/stats`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch stats');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Get stats error:', error);
      throw error;
    }
  }
};
