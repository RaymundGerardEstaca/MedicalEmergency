#!/bin/bash

echo "🔧 Fixing connection issues..."

# 1. Setup environment if needed
if ! command -v adb &> /dev/null; then
    source "$(dirname "$0")/setup-android.sh"
fi

# 2. Run ADB Reverse
# This maps the phone's port 8081 to the computer's port 8081 over USB.
# This allows the phone to connect even if they are on different WiFi networks.
echo "🔄 Running adb reverse for Metro Bundler (8081)..."
adb reverse tcp:8081 tcp:8081

# 3. Also reverse the port for your future Python backend (8000)
echo "🔄 Running adb reverse for Backend (8000)..."
adb reverse tcp:8000 tcp:8000

echo "✅ Port forwarding setup complete."
echo ""
echo "📱 ACTION REQUIRED ON PHONE:"
echo "1. Shake your phone (or press 'r' in the terminal if connected)."
echo "2. Tap 'Reload' on the error screen."
echo "3. If it still fails, ensure your phone is connected to the SAME WiFi as your PC (10.0.0.x)."

