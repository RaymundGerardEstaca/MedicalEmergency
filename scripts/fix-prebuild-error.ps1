# Fix TAR_BAD_ARCHIVE error during Expo prebuild
Set-Location "$PSScriptRoot\.."
# This script clears all caches and fixes corrupted downloads

Write-Host "=== Fixing Expo Prebuild TAR Error ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Remove any partial android/ios folders
Write-Host "Step 1: Removing any existing native folders..." -ForegroundColor Yellow
if (Test-Path "android") {
    Remove-Item -Recurse -Force "android"
    Write-Host "  Removed android folder" -ForegroundColor Green
}
if (Test-Path "ios") {
    Remove-Item -Recurse -Force "ios"
    Write-Host "  Removed ios folder" -ForegroundColor Green
}

# Step 2: Clear npm cache
Write-Host ""
Write-Host "Step 2: Clearing npm cache..." -ForegroundColor Yellow
npm cache clean --force
Write-Host "  npm cache cleared" -ForegroundColor Green

# Step 3: Clear Expo cache
Write-Host ""
Write-Host "Step 3: Clearing Expo cache..." -ForegroundColor Yellow
$expoCache = "$env:USERPROFILE\.expo"
if (Test-Path $expoCache) {
    Remove-Item -Recurse -Force $expoCache -ErrorAction SilentlyContinue
    Write-Host "  Removed user Expo cache" -ForegroundColor Green
}
if (Test-Path ".expo") {
    Remove-Item -Recurse -Force ".expo" -ErrorAction SilentlyContinue
    Write-Host "  Removed project Expo cache" -ForegroundColor Green
}

# Step 4: Clear node_modules and package-lock
Write-Host ""
Write-Host "Step 4: Removing node_modules..." -ForegroundColor Yellow
if (Test-Path "node_modules") {
    Remove-Item -Recurse -Force "node_modules"
    Write-Host "  Removed node_modules" -ForegroundColor Green
}
if (Test-Path "package-lock.json") {
    Remove-Item -Force "package-lock.json"
    Write-Host "  Removed package-lock.json" -ForegroundColor Green
}

# Step 5: Reinstall dependencies
Write-Host ""
Write-Host "Step 5: Reinstalling dependencies..." -ForegroundColor Yellow
Write-Host "  This may take a few minutes..." -ForegroundColor Gray
npm install

Write-Host ""
Write-Host "=== Cleanup Complete! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Try prebuild again:"
Write-Host "   npx expo prebuild --clean --platform android" -ForegroundColor White
Write-Host ""
Write-Host "2. If it still fails, use EAS cloud build instead:"
Write-Host "   npx eas build --platform android --profile development" -ForegroundColor White
Write-Host ""
Write-Host "3. Or try with verbose logging to see what's failing:"
Write-Host "   npx expo prebuild --clean --platform android --verbose" -ForegroundColor White
Write-Host ""

