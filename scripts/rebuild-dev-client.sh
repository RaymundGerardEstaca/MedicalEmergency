#!/bin/bash
cd "$(dirname "$0")/.."

# Rebuild script for Expo Dev Client
# This fixes the "java.lang.String cannot be cast to ReadableArray" error
# by ensuring a clean native build

echo "🧹 Cleaning Expo cache and node_modules..."
rm -rf node_modules
rm -rf .expo
rm -rf .expo-shared

echo "📦 Reinstalling dependencies..."
npm install

echo "🔄 Clearing Metro bundler cache..."
npx expo start --clear

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "📱 Next steps:"
echo "1. Stop the Metro bundler (Ctrl+C)"
echo "2. Rebuild your dev client:"
echo "   - For Android: npx expo run:android"
echo "   - For iOS: npx expo run:ios"
echo ""
echo "⚠️  IMPORTANT: Uninstall the old app from your device before rebuilding!"

