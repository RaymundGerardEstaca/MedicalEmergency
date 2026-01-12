# Frontend Development Guide
## React Native CCTV Mobile Application

**Framework:** React Native + Expo  
**Language:** TypeScript  
**Version:** 1.0.0

---

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Navigation Structure](#navigation-structure)
3. [Screens](#screens)
4. [Components](#components)
5. [Services](#services)
6. [State Management](#state-management)
7. [Styling Guide](#styling-guide)
8. [Testing](#testing)
9. [Best Practices](#best-practices)

---

## 🏗️ Architecture Overview

### App Structure

```
App.tsx (Root)
   │
   ├─ NavigationContainer
   │     │
   │     └─ Stack.Navigator
   │           │
   │           ├─ SplashScreen (Entry Point)
   │           ├─ LoginScreen
   │           ├─ DevicesListScreen (Main)
   │           ├─ DeviceDiscoveryScreen
   │           ├─ WiFiProvisioningScreen
   │           ├─ SoftAPProvisioningScreen
   │           ├─ CameraConfigScreen
   │           └─ StreamViewerScreen
   │
   └─ StatusBar
```

### Data Flow

```
┌─────────────┐
│   Screen    │
└──────┬──────┘
       │
       ├─ Uses Service ─────┐
       │                    │
       ├─ Updates State     │
       │                    ▼
       │              ┌────────────┐
       │              │  Service   │
       │              │  - API     │
       │              │  - BLE     │
       │              │  - Storage │
       │              └─────┬──────┘
       │                    │
       │                    ├─ HTTP Request
       │                    ├─ BLE Operation
       │                    └─ SecureStore
       │                          │
       ▼                          ▼
┌──────────────┐          ┌─────────────┐
│  Component   │          │   Backend   │
└──────────────┘          └─────────────┘
```

---

## 🧭 Navigation Structure

### Route Parameters

Defined in `App.tsx`:

```typescript
export type RootStackParamList = {
  Splash: undefined;
  Login: undefined;
  DevicesList: undefined;
  DeviceDiscovery: undefined;
  WiFiProvisioning: { device: BLEDevice };
  SoftAPProvisioning: { targetSSID?: string };
  CameraConfig: { 
    device?: BLEDevice; 
    existingConfig?: CameraConfig 
  };
  StreamViewer: { 
    device?: CCTVDevice; 
    cameraConfig?: CameraConfig 
  };
};
```

### Navigation Flow

```
Splash
  └─> Login
       └─> DevicesList (Main Hub)
            ├─> DeviceDiscovery
            │    ├─> WiFiProvisioning
            │    │    └─> CameraConfig
            │    └─> SoftAPProvisioning
            │         └─> CameraConfig
            │
            ├─> CameraConfig (Edit Mode)
            │
            └─> StreamViewer
```

### Navigation Hook Usage

```typescript
import { useNavigation } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import { RootStackParamList } from '../App';

type NavigationProp = StackNavigationProp<RootStackParamList>;

const MyScreen = () => {
  const navigation = useNavigation<NavigationProp>();
  
  const handleNavigate = () => {
    navigation.navigate('StreamViewer', { device: myDevice });
  };
  
  const handleGoBack = () => {
    navigation.goBack();
  };
  
  return ( /* JSX */ );
};
```

---

## 📱 Screens

### 1. SplashScreen

**File:** `src/screens/SplashScreen.tsx`

**Purpose:** Initial loading screen with app branding.

**Key Features:**
- Display app logo
- Check authentication status
- Auto-navigate after 2 seconds

**Implementation:**
```typescript
const SplashScreen = () => {
  const navigation = useNavigation<NavigationProp>();

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = await DeviceStorageService.getAuthToken();
    
    setTimeout(() => {
      if (token) {
        navigation.replace('DevicesList');
      } else {
        navigation.replace('Login');
      }
    }, 2000);
  };

  return (
    <View style={styles.container}>
      <Image source={require('../assets/logo.png')} />
      <ActivityIndicator size="large" color="#007AFF" />
    </View>
  );
};
```

**Styling:**
- Full screen black background
- Centered logo
- Loading indicator below logo

---

### 2. LoginScreen

**File:** `src/screens/LoginScreen.tsx`

**Purpose:** User authentication with email/password and Google Sign-In.

**Key Features:**
- Email/password input
- Form validation
- Google OAuth integration
- "Remember Me" option
- Error handling

**State Management:**
```typescript
interface LoginState {
  email: string;
  password: string;
  loading: boolean;
  error: string | null;
  rememberMe: boolean;
}
```

**API Integration:**
```typescript
const handleLogin = async () => {
  setLoading(true);
  setError(null);

  try {
    const response = await BackendAPIService.login(email, password);
    
    await DeviceStorageService.saveAuthToken(response.token);
    
    if (rememberMe) {
      await AsyncStorage.setItem('rememberedEmail', email);
    }
    
    navigation.replace('DevicesList');
  } catch (err) {
    setError('Invalid credentials. Please try again.');
  } finally {
    setLoading(false);
  }
};
```

**Google Sign-In:**
```typescript
import {
  GoogleSignin,
  statusCodes,
} from '@react-native-google-signin/google-signin';

const handleGoogleSignIn = async () => {
  try {
    await GoogleSignin.hasPlayServices();
    const userInfo = await GoogleSignin.signIn();
    
    // Send to backend for verification
    const response = await BackendAPIService.googleAuth(userInfo.idToken);
    
    await DeviceStorageService.saveAuthToken(response.token);
    navigation.replace('DevicesList');
  } catch (error) {
    if (error.code === statusCodes.SIGN_IN_CANCELLED) {
      console.log('User cancelled sign-in');
    }
  }
};
```

**UI Components:**
- TextInput fields with icons
- Submit button with loading state
- Google Sign-In button
- "Forgot Password?" link
- "Create Account" link

---

### 3. DevicesListScreen

**File:** `src/screens/DevicesListScreen.tsx`

**Purpose:** Main dashboard showing all configured cameras.

**Key Features:**
- List of devices with status
- Pull-to-refresh
- Add camera button
- Navigate to stream viewer
- Device heartbeat polling

**State:**
```typescript
interface DevicesListState {
  devices: CCTVDevice[];
  loading: boolean;
  refreshing: boolean;
  error: string | null;
}
```

**Device Loading:**
```typescript
const loadDevices = async () => {
  try {
    const devices = await BackendAPIService.getDevices();
    setDevices(devices);
    
    // Start heartbeat polling
    startHeartbeatPolling(devices);
  } catch (err) {
    setError('Failed to load devices');
  }
};

const startHeartbeatPolling = (devices: CCTVDevice[]) => {
  const interval = setInterval(async () => {
    for (const device of devices) {
      try {
        const status = await BackendAPIService.deviceHeartbeat(device.device_id);
        updateDeviceStatus(device.device_id, status.isOnline);
      } catch (err) {
        // Device offline
      }
    }
  }, 30000); // Every 30 seconds
  
  return () => clearInterval(interval);
};
```

**Render:**
```typescript
<FlatList
  data={devices}
  keyExtractor={(item) => item.device_id}
  renderItem={({ item }) => (
    <DeviceListItem
      device={item}
      onPress={() => navigation.navigate('StreamViewer', { device: item })}
      onLongPress={() => handleEdit(item)}
    />
  )}
  refreshControl={
    <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
  }
  ListEmptyComponent={
    <View style={styles.emptyState}>
      <Text>No cameras added yet</Text>
      <Button title="Add Camera" onPress={handleAddCamera} />
    </View>
  }
/>
```

---

### 4. DeviceDiscoveryScreen

**File:** `src/screens/DeviceDiscoveryScreen.tsx`

**Purpose:** Discover cameras via BLE scanning.

**Key Features:**
- BLE device scanning
- Device list with signal strength
- Connect to device
- Filter by device type
- SoftAP fallback option

**BLE Scanning:**
```typescript
import { BLEProvisioningService } from '../services/BLEProvisioningService';

const [devices, setDevices] = useState<BLEDevice[]>([]);
const [scanning, setScanning] = useState(false);

const startScan = async () => {
  setScanning(true);
  setDevices([]);
  
  try {
    await BLEProvisioningService.startScan((device) => {
      setDevices(prev => {
        // Avoid duplicates
        if (prev.find(d => d.id === device.id)) return prev;
        return [...prev, device];
      });
    });
    
    // Stop after 10 seconds
    setTimeout(() => {
      BLEProvisioningService.stopScan();
      setScanning(false);
    }, 10000);
  } catch (err) {
    Alert.alert('Error', 'Failed to start BLE scan');
  }
};

const handleConnect = async (device: BLEDevice) => {
  try {
    await BLEProvisioningService.connect(device.id);
    navigation.navigate('WiFiProvisioning', { device });
  } catch (err) {
    Alert.alert('Error', 'Failed to connect to device');
  }
};
```

**UI:**
```typescript
<View>
  <Button 
    title={scanning ? 'Scanning...' : 'Start Scan'} 
    onPress={startScan}
    disabled={scanning}
  />
  
  <FlatList
    data={devices}
    renderItem={({ item }) => (
      <TouchableOpacity onPress={() => handleConnect(item)}>
        <View style={styles.deviceItem}>
          <Text>{item.name}</Text>
          <Text>Signal: {item.rssi} dBm</Text>
          <Icon name="bluetooth" />
        </View>
      </TouchableOpacity>
    )}
  />
  
  <Button 
    title="Use SoftAP Method" 
    onPress={() => navigation.navigate('SoftAPProvisioning')}
  />
</View>
```

---

### 5. WiFiProvisioningScreen

**File:** `src/screens/WiFiProvisioningScreen.tsx`

**Purpose:** Configure camera WiFi via BLE.

**Key Features:**
- WiFi network list
- Password input
- Send credentials via BLE
- Connection progress
- Error handling

**WiFi Configuration:**
```typescript
const [ssid, setSSID] = useState('');
const [password, setPassword] = useState('');
const [sending, setSending] = useState(false);

const handleSendCredentials = async () => {
  setSending(true);
  
  try {
    const success = await BLEProvisioningService.sendWiFiCredentials(ssid, password);
    
    if (success) {
      // Wait for device to connect
      await waitForConnection();
      
      Alert.alert('Success', 'Camera connected to WiFi', [
        { text: 'OK', onPress: () => navigation.navigate('CameraConfig', { device }) }
      ]);
    } else {
      Alert.alert('Error', 'Failed to send credentials');
    }
  } catch (err) {
    Alert.alert('Error', err.message);
  } finally {
    setSending(false);
  }
};

const waitForConnection = async () => {
  return new Promise((resolve, reject) => {
    let attempts = 0;
    const maxAttempts = 30; // 30 seconds
    
    const interval = setInterval(async () => {
      attempts++;
      
      const status = await BLEProvisioningService.getConnectionStatus();
      
      if (status.connected) {
        clearInterval(interval);
        resolve(status);
      } else if (attempts >= maxAttempts) {
        clearInterval(interval);
        reject(new Error('Connection timeout'));
      }
    }, 1000);
  });
};
```

---

### 6. SoftAPProvisioningScreen

**File:** `src/screens/SoftAPProvisioningScreen.tsx`

**Purpose:** Configure camera WiFi via SoftAP (WiFi hotspot method).

**Process:**
1. User connects to camera's WiFi hotspot (e.g., "ESP32-CAM-XXXX")
2. App detects connection to camera's AP
3. App sends WiFi credentials via HTTP POST
4. Camera connects to target WiFi
5. App instructs user to reconnect to home WiFi

**Implementation:**
```typescript
import { SoftAPProvisioningService } from '../services/SoftAPProvisioningService';

const [step, setStep] = useState<'connect' | 'configure' | 'complete'>('connect');

// Step 1: Detect connection to camera's AP
useEffect(() => {
  const checkConnection = async () => {
    const currentSSID = await WiFiDetectionService.getCurrentSSID();
    
    if (currentSSID?.startsWith('ESP32-CAM-')) {
      setStep('configure');
    }
  };
  
  const interval = setInterval(checkConnection, 2000);
  return () => clearInterval(interval);
}, []);

// Step 2: Send credentials
const handleConfigure = async () => {
  try {
    await SoftAPProvisioningService.sendCredentials(targetSSID, password);
    setStep('complete');
  } catch (err) {
    Alert.alert('Error', 'Failed to configure camera');
  }
};
```

**UI Steps:**
```typescript
{step === 'connect' && (
  <View>
    <Text>Step 1: Connect to Camera's WiFi</Text>
    <Text>Network Name: ESP32-CAM-XXXX</Text>
    <Button title="Open WiFi Settings" onPress={openWiFiSettings} />
  </View>
)}

{step === 'configure' && (
  <View>
    <Text>Step 2: Enter Target WiFi</Text>
    <TextInput placeholder="WiFi Name" value={targetSSID} />
    <TextInput placeholder="Password" secureTextEntry value={password} />
    <Button title="Configure" onPress={handleConfigure} />
  </View>
)}

{step === 'complete' && (
  <View>
    <Text>✓ Camera Configured!</Text>
    <Text>Reconnect to your home WiFi</Text>
    <Button title="Continue" onPress={handleContinue} />
  </View>
)}
```

---

### 7. CameraConfigScreen

**File:** `src/screens/CameraConfigScreen.tsx`

**Purpose:** Configure camera settings (name, IP, RTSP URL).

**Key Features:**
- Device name input
- IP address configuration
- RTSP URL and credentials
- Connection test
- Save configuration

**Form State:**
```typescript
interface CameraConfigForm {
  name: string;
  ipAddress: string;
  rtspUrl: string;
  username: string;
  password: string;
}
```

**Validation:**
```typescript
const validateForm = (): boolean => {
  // IP Address validation
  const ipRegex = /^(\d{1,3}\.){3}\d{1,3}$/;
  if (!ipRegex.test(ipAddress)) {
    Alert.alert('Error', 'Invalid IP address format');
    return false;
  }
  
  // RTSP URL validation
  if (!rtspUrl.startsWith('rtsp://')) {
    Alert.alert('Error', 'RTSP URL must start with rtsp://');
    return false;
  }
  
  return true;
};
```

**Connection Test:**
```typescript
const testConnection = async () => {
  setTesting(true);
  
  try {
    const result = await BackendAPIService.checkConnectivity(rtspUrl);
    
    if (result.reachable) {
      Alert.alert('Success', `Connection successful (${result.latency_ms}ms)`);
    } else {
      Alert.alert('Error', 'Cannot reach camera');
    }
  } catch (err) {
    Alert.alert('Error', 'Connection test failed');
  } finally {
    setTesting(false);
  }
};
```

**Save Configuration:**
```typescript
const handleSave = async () => {
  if (!validateForm()) return;
  
  setSaving(true);
  
  try {
    const deviceData = {
      bleId: device?.id || `manual_${Date.now()}`,
      name,
      ipAddress,
      rtspUrl: buildRTSPUrl(ipAddress, username, password)
    };
    
    const saved = await BackendAPIService.registerDevice(deviceData);
    await DeviceStorageService.saveDevice(saved);
    
    Alert.alert('Success', 'Camera saved successfully', [
      { text: 'OK', onPress: () => navigation.navigate('DevicesList') }
    ]);
  } catch (err) {
    Alert.alert('Error', 'Failed to save camera');
  } finally {
    setSaving(false);
  }
};

const buildRTSPUrl = (ip: string, user: string, pass: string): string => {
  return `rtsp://${user}:${pass}@${ip}:554/stream1`;
};
```

---

### 8. StreamViewerScreen

**File:** `src/screens/StreamViewerScreen.tsx`

**Purpose:** View live camera stream with HLS playback.

**Key Features:**
- HLS video playback
- Loading state
- Live indicator
- Mute/unmute
- Pull-to-refresh
- Error handling
- Alert snapshots carousel

**Stream Management:**
```typescript
import { Video, ResizeMode } from 'expo-av';

const [streamUrl, setStreamUrl] = useState<string | null>(null);
const [loading, setLoading] = useState(true);
const [isLive, setIsLive] = useState(false);
const [muted, setMuted] = useState(true);
const videoRef = useRef<Video>(null);

const startStream = async () => {
  setLoading(true);
  
  try {
    const response = await BackendAPIService.startStream(device.rtspUrl);
    
    setStreamUrl(response.hls_url);
    
    // Wait for HLS playlist to be ready
    setTimeout(() => {
      setIsLive(true);
      setLoading(false);
    }, 4000);
  } catch (err) {
    setLoading(false);
    Alert.alert('Error', 'Failed to start stream');
  }
};

useEffect(() => {
  startStream();
  
  return () => {
    stopStream();
  };
}, []);

const stopStream = async () => {
  try {
    await BackendAPIService.stopStream(device.device_id);
  } catch (err) {
    console.error('Failed to stop stream:', err);
  }
};
```

**Video Player:**
```typescript
<View style={styles.videoContainer}>
  {loading && (
    <View style={styles.loadingOverlay}>
      <ActivityIndicator size="large" color="#fff" />
      <Text style={styles.loadingText}>Loading stream...</Text>
    </View>
  )}
  
  {streamUrl && (
    <Video
      ref={videoRef}
      source={{ uri: streamUrl }}
      style={styles.video}
      useNativeControls={false}
      resizeMode={ResizeMode.CONTAIN}
      isLooping
      isMuted={muted}
      shouldPlay
      onLoad={() => console.log('Stream loaded')}
      onError={(error) => console.error('Stream error:', error)}
    />
  )}
  
  {isLive && (
    <View style={styles.liveBadge}>
      <View style={[styles.liveIndicator, { opacity: flashAnimation }]} />
      <Text style={styles.liveText}>LIVE</Text>
    </View>
  )}
  
  <TouchableOpacity 
    style={styles.muteButton}
    onPress={() => setMuted(!muted)}
  >
    <Icon name={muted ? 'volume-mute' : 'volume-high'} size={24} />
  </TouchableOpacity>
</View>
```

**Live Indicator Animation:**
```typescript
const [flashAnimation] = useState(new Animated.Value(1));

useEffect(() => {
  Animated.loop(
    Animated.sequence([
      Animated.timing(flashAnimation, {
        toValue: 0.3,
        duration: 500,
        useNativeDriver: true,
      }),
      Animated.timing(flashAnimation, {
        toValue: 1,
        duration: 500,
        useNativeDriver: true,
      }),
    ])
  ).start();
}, []);
```

**Pull to Refresh:**
```typescript
const [refreshing, setRefreshing] = useState(false);

const handleRefresh = async () => {
  setRefreshing(true);
  
  await stopStream();
  await startStream();
  
  setRefreshing(false);
};

<ScrollView
  refreshControl={
    <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
  }
>
  {/* Video player */}
</ScrollView>
```

---

## 🧩 Components

### AlarmModal

**File:** `src/components/AlarmModal.tsx`

**Purpose:** Full-screen critical alarm overlay.

**Props:**
```typescript
interface AlarmModalProps {
  visible: boolean;
  onDismiss: () => void;
  snapshot?: string;
  timestamp: Date;
  detectedObject: string;
}
```

**Features:**
- Red/white flashing background (2Hz)
- Large warning text
- Snapshot preview
- iPhone-style slide-to-dismiss
- Siren sound playback
- Haptic feedback

**Implementation:**
```typescript
const AlarmModal: React.FC<AlarmModalProps> = ({
  visible,
  onDismiss,
  snapshot,
  timestamp,
  detectedObject,
}) => {
  const [flashColor, setFlashColor] = useState('#FF0000');
  const [slideX] = useState(new Animated.Value(0));
  const soundObject = useRef(new Audio.Sound());
  
  // Flashing animation
  useEffect(() => {
    if (!visible) return;
    
    const interval = setInterval(() => {
      setFlashColor(prev => prev === '#FF0000' ? '#FFFFFF' : '#FF0000');
    }, 500); // 2Hz
    
    return () => clearInterval(interval);
  }, [visible]);
  
  // Play siren
  useEffect(() => {
    if (visible) {
      playSiren();
    } else {
      stopSiren();
    }
  }, [visible]);
  
  const playSiren = async () => {
    try {
      await soundObject.current.loadAsync(require('../assets/siren.mp3'));
      await soundObject.current.setIsLoopingAsync(true);
      await soundObject.current.playAsync();
    } catch (err) {
      console.error('Failed to play siren:', err);
    }
  };
  
  const stopSiren = async () => {
    try {
      await soundObject.current.stopAsync();
      await soundObject.current.unloadAsync();
    } catch (err) {}
  };
  
  // Slide to dismiss
  const handleSlide = (gestureState: PanResponderGestureState) => {
    if (gestureState.dx > 200) {
      Animated.timing(slideX, {
        toValue: 300,
        duration: 200,
        useNativeDriver: true,
      }).start(() => {
        onDismiss();
        slideX.setValue(0);
      });
    }
  };
  
  return (
    <Modal visible={visible} animationType="fade" transparent={false}>
      <View style={[styles.container, { backgroundColor: flashColor }]}>
        <Text style={styles.warning}>⚠️ INTRUDER DETECTED</Text>
        
        {snapshot && (
          <Image source={{ uri: snapshot }} style={styles.snapshot} />
        )}
        
        <Text style={styles.object}>{detectedObject}</Text>
        <Text style={styles.time}>{timestamp.toLocaleTimeString()}</Text>
        
        <SliderControl onSlide={handleSlide} />
      </View>
    </Modal>
  );
};
```

---

### DeviceListItem

**File:** `src/components/DeviceListItem.tsx`

**Purpose:** Device card for the devices list.

**Props:**
```typescript
interface DeviceListItemProps {
  device: CCTVDevice;
  onPress: () => void;
  onLongPress?: () => void;
}
```

**Render:**
```typescript
<TouchableOpacity onPress={onPress} onLongPress={onLongPress}>
  <View style={styles.card}>
    <View style={styles.iconContainer}>
      <Icon name="videocam" size={32} color="#007AFF" />
      <View style={[
        styles.statusDot,
        { backgroundColor: device.isOnline ? '#4CAF50' : '#F44336' }
      ]} />
    </View>
    
    <View style={styles.info}>
      <Text style={styles.name}>{device.name}</Text>
      <Text style={styles.ip}>{device.ipAddress}</Text>
      <Text style={styles.lastSeen}>
        {device.isOnline ? 'Online' : `Last seen: ${formatTime(device.lastSeen)}`}
      </Text>
    </View>
    
    <Icon name="chevron-forward" size={24} color="#999" />
  </View>
</TouchableOpacity>
```

---

## 🛠️ Services

### BackendAPIService

**File:** `src/services/BackendAPIService.ts`

**Purpose:** HTTP client for backend communication.

**Setup:**
```typescript
class BackendAPIService {
  private static baseURL = 'http://192.168.1.100:8000';
  private static authToken: string | null = null;
  
  static setAuthToken(token: string) {
    this.authToken = token;
  }
  
  private static async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...(this.authToken && { Authorization: `Bearer ${this.authToken}` }),
      ...options.headers,
    };
    
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers,
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Request failed');
    }
    
    return response.json();
  }
}
```

---

### BLEProvisioningService

**File:** `src/services/BLEProvisioningService.ts`

**Purpose:** Bluetooth Low Energy communication.

**Setup:**
```typescript
import { BleManager, Device } from 'react-native-ble-plx';

class BLEProvisioningService {
  private static manager: BleManager;
  private static connectedDevice: Device | null = null;
  
  static init() {
    this.manager = new BleManager();
  }
  
  static async startScan(callback: (device: BLEDevice) => void) {
    this.manager.startDeviceScan(null, null, (error, device) => {
      if (error) {
        console.error('BLE scan error:', error);
        return;
      }
      
      if (device && device.name?.includes('ESP32')) {
        callback({
          id: device.id,
          name: device.name,
          rssi: device.rssi || 0,
        });
      }
    });
  }
}
```

---

## 🎨 Styling Guide

### Theme

```typescript
export const Colors = {
  primary: '#007AFF',
  secondary: '#5856D6',
  success: '#4CAF50',
  error: '#F44336',
  warning: '#FF9800',
  background: '#000000',
  surface: '#1C1C1E',
  text: '#FFFFFF',
  textSecondary: '#999999',
  border: '#333333',
};

export const Spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
};

export const Typography = {
  h1: { fontSize: 32, fontWeight: 'bold' },
  h2: { fontSize: 24, fontWeight: 'bold' },
  body: { fontSize: 16 },
  caption: { fontSize: 12, color: Colors.textSecondary },
};
```

---

## ✅ Best Practices

1. **Use TypeScript** for type safety
2. **Extract reusable components**
3. **Handle errors gracefully**
4. **Show loading states**
5. **Clean up effects and intervals**
6. **Optimize FlatList with proper keys**
7. **Use SecureStore for sensitive data**
8. **Test on both iOS and Android**

---

**Last Updated:** January 12, 2026  
**Version:** 1.0.0
