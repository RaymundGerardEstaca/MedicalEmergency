# Rebuild script for Expo Dev Client (PowerShell)
Set-Location "$PSScriptRoot\.."
# This fixes the "java.lang.String cannot be cast to ReadableArray" error

Write-Host "Cleaning Expo cache and node_modules..." -ForegroundColor Yellow

if (Test-Path "node_modules") {
    Remove-Item -Recurse -Force "node_modules"
    Write-Host "Removed node_modules" -ForegroundColor Green
}
if (Test-Path ".expo") {
    Remove-Item -Recurse -Force ".expo"
    Write-Host "Removed .expo" -ForegroundColor Green
}
if (Test-Path ".expo-shared") {
    Remove-Item -Recurse -Force ".expo-shared"
    Write-Host "Removed .expo-shared" -ForegroundColor Green
}

Write-Host ""
Write-Host "Reinstalling dependencies..." -ForegroundColor Yellow
npm install

Write-Host ""
Write-Host "Cleanup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Stop the Metro bundler (Ctrl+C if running)"
Write-Host "2. Uninstall the old app from your Android device"
Write-Host "3. Rebuild your dev client:"
Write-Host "   npx expo run:android"
Write-Host "4. Start Metro with cleared cache:"
Write-Host "   npx expo start --clear"
Write-Host ""
