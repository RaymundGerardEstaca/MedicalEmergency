#!/bin/bash

# Add Android SDK to PATH
export ANDROID_HOME="/c/Users/LOQ/AppData/Local/Android/Sdk"
export PATH="$PATH:$ANDROID_HOME/emulator:$ANDROID_HOME/platform-tools"

echo "🔍 Checking available emulators..."
emulator -list-avds

echo ""
echo "📱 To start an emulator manually:"
echo "1. Open Android Studio"
echo "2. Go to: Tools → Device Manager"
echo "3. Click the ▶️ Play button next to 'Medium_Phone_API_36.0'"
echo "4. Wait for it to fully boot (home screen appears)"
echo "5. Then run: npx expo run:android"
echo ""
echo "OR use this command to start it from terminal:"
echo "emulator -avd Medium_Phone_API_36.0 &"

