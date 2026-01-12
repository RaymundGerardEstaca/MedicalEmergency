#!/bin/bash

# Add Android SDK platform-tools to PATH
export ANDROID_HOME="/c/Users/LOQ/AppData/Local/Android/Sdk"
export PATH="$PATH:$ANDROID_HOME/platform-tools"

echo "🔍 Checking for connected Android devices..."
adb devices

echo ""
echo "⚠️  If the list above is empty:"
echo "1. Connect your Android phone via USB."
echo "2. Ensure 'USB Debugging' is ENABLED in Developer Options."
echo "3. Check your phone screen for a prompt 'Allow USB debugging?' and tap ALLOW."
echo "4. If using an emulator, launch it from Android Studio -> Device Manager."

