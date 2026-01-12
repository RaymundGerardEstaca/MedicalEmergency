@echo off
cd /d "%~dp0\.."
REM Rebuild script for Expo Dev Client (Windows)
REM This fixes the "java.lang.String cannot be cast to ReadableArray" error
REM by ensuring a clean native build

echo Cleaning Expo cache and node_modules...
if exist node_modules rmdir /s /q node_modules
if exist .expo rmdir /s /q .expo
if exist .expo-shared rmdir /s /q .expo-shared

echo Reinstalling dependencies...
call npm install

echo.
echo Cleanup complete!
echo.
echo Next steps:
echo 1. Stop the Metro bundler (Ctrl+C)
echo 2. Rebuild your dev client:
echo    - For Android: npx expo run:android
echo    - For iOS: npx expo run:ios
echo.
echo IMPORTANT: Uninstall the old app from your device before rebuilding!
pause

