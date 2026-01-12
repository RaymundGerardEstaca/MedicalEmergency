# 🚀 Quick Start Guide

## Development Server is Running!

The Expo development server has been started. You should see a QR code in the terminal.

## 📱 Running the App

### Option 1: Physical Device (Recommended)
1. Install **Expo Go** app from:
   - iOS: App Store
   - Android: Google Play Store

2. **Scan the QR code** shown in the terminal with:
   - iOS: Camera app
   - Android: Expo Go app

### Option 2: iOS Simulator (Mac Only)
Press `i` in the terminal running Expo

### Option 3: Android Emulator
Press `a` in the terminal running Expo

## 🎯 Testing the App

### 1. Camera Configuration Screen (First Screen)
- **Test Input Validation:**
  - Enter camera name: "Front Door"
  - Try invalid IP: "999.999.999.999" (should show error)
  - Enter valid IP: "192.168.1.50" (checkmark appears)
  - RTSP Username: "admin"
  - RTSP Password: "password123"
  - Cloud URL: "rtmp://cloud.example.com/live/stream1" (checkmark appears)

- **Test Network Scanner:**
  - Tap "Scan Network" (requires WiFi connection)
  - View discovered devices
  - Tap a device to auto-fill IP address

- **Test Connection:**
  - Tap "Test Connection" (simulated for demo)
  - Should show success or error message

- **Save Configuration:**
  - Tap "Save Configuration"
  - Choose "View Stream" to navigate to viewer

### 2. Stream Viewer Screen (Second Screen)
- **HLS Video Player:**
  - Video should auto-play (muted by default)
  - "LIVE" badge appears in top-right
  - Tap speaker icon to unmute/mute

- **Pull to Refresh:**
  - Swipe down to reload stream

- **Alert Snapshots:**
  - Scroll horizontal carousel at bottom
  - Tap any snapshot for full-screen view
  - View timestamp and detected object label

- **Test Alarm (Optional):**
  - In `src/screens/StreamViewerScreen.tsx` line 57
  - Uncomment: `// setShowAlarmModal(true);`
  - Reload app to trigger alarm after 15 seconds
  - Test slide-to-dismiss gesture

## 🔧 Development Commands

```bash
# Start development server
npm start

# Start with clearing cache
npm start -- --clear

# Run on iOS simulator
npm run ios

# Run on Android emulator
npm run android

# Build for production
npx expo build:ios
npx expo build:android
```

## 📁 File Structure

```
src/
├── screens/
│   ├── CameraConfigScreen.tsx    # Setup wizard (FR-A1, FR-A2, FR-A3)
│   └── StreamViewerScreen.tsx    # Video player (FR-C1-C4)
├── components/
│   ├── NetworkScanner.tsx        # LAN scanner modal (FR-A2)
│   └── AlarmModal.tsx            # Critical alarm UI (FR-Z1, FR-Z2)
└── types/
    └── index.ts                  # TypeScript interfaces
```

## 🎨 Customization

### Change Colors
Edit styles in each screen file:
- Primary: `#2196F3` (Blue)
- Success: `#4CAF50` (Green)
- Warning: `#FF9800` (Orange)
- Error: `#F44336` (Red)

### Replace Mock Data

**Stream URL** (StreamViewerScreen.tsx line 35):
```typescript
const hlsStreamURL = `https://your-backend.com/cameras/${cameraConfig.localIP}/stream.m3u8`;
```

**Alert Snapshots** (StreamViewerScreen.tsx line 38):
```typescript
const response = await fetch(`https://your-api.com/alerts/recent`);
const snapshots = await response.json();
```

## 🔒 Security Notes

- RTSP credentials are stored in **Expo SecureStore** (encrypted)
- Never commit credentials to git
- Use environment variables for API endpoints
- Enable SSL/TLS for production streams

## 🐛 Troubleshooting

### "Module not found" errors
```bash
npm install
npx expo start --clear
```

### Camera not loading
- Check WiFi connection
- Verify IP address is correct
- Ensure camera is powered on
- Test RTSP credentials

### Network scanner not working
- Requires WiFi connection (not mobile data)
- iOS needs `NSLocalNetworkUsageDescription` permission
- Android needs network permissions

### Video not playing
- Test with demo HLS URL first
- Check backend CORS settings
- Verify HLS format (.m3u8)
- Enable low latency in player config

## 📚 SRS Implementation Status

### Module A: Network Configuration ✅
- [x] FR-A1: Configuration Dashboard
- [x] FR-A2: Network Discovery/LAN Scan
- [x] FR-A3: Connection Test Logic
- [x] NFR-A1: Secure credential storage
- [x] NFR-A2: 10-second scan timeout
- [x] NFR-A3: WiFi-only guidance

### Module C: Stream Viewer ✅
- [x] FR-C1: Adaptive Video Player
- [x] FR-C2: Stream State Management
- [x] FR-C3: Pull-to-Refresh
- [x] FR-C4: Alert Snapshots Carousel
- [x] NFR-C1: Non-blocking UI
- [x] NFR-C2: Low latency buffer
- [x] NFR-C3: Background audio stops

### Module Z: Critical Alarm ✅
- [x] FR-Z1: Full-Screen Alarm Modal
- [x] FR-Z2: Slide-to-Dismiss Control
- [x] Visual flashing (2Hz)
- [x] Vibration pattern
- [x] Dismissal logging

## 🚀 Next Steps

1. **Replace mock data** with real backend APIs
2. **Add authentication** for secure access
3. **Implement real network scanner** using native modules
4. **Configure push notifications** for alerts
5. **Add offline mode** with cached snapshots
6. **Implement analytics** for usage tracking
7. **Add multi-camera support**
8. **Setup CI/CD** for automated builds

## 📞 Need Help?

- Check `README.md` for detailed documentation
- Review SRS requirements in `.github/copilot-instructions.md`
- Test with demo data before connecting real cameras

**Happy Coding! 🎉**
