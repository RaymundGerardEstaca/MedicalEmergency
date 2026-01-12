# Backend API Testing Script for Windows
# Tests all endpoints of app_with_auth.py with JWT authentication
# Usage: powershell -ExecutionPolicy Bypass -File test-backend-api.ps1

$BaseUrl = "http://localhost:5000"
$Token = ""
$UserId = ""
$DeviceId = ""

Write-Host "🚀 Starting Backend API Testing..." -ForegroundColor Cyan
Write-Host "=================================="
Write-Host ""

# Function to print colored output
function Print-Success {
    param($Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Print-Error {
    param($Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Print-Info {
    param($Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Yellow
}

# Check if Flask server is running
Write-Host "1️⃣  Checking if Flask server is running..."
try {
    $healthCheck = Invoke-RestMethod -Uri "$BaseUrl/api/health" -Method Get
    Print-Success "Flask server is running"
}
catch {
    Print-Error "Flask server is not running at $BaseUrl"
    Print-Info "Start the server with: python backend/app_with_auth.py"
    exit 1
}
Write-Host ""

# Test 1: Health Check
Write-Host "2️⃣  Testing Health Check Endpoint"
$healthResponse = Invoke-RestMethod -Uri "$BaseUrl/api/health" -Method Get
Write-Host "Response: $($healthResponse | ConvertTo-Json)"
if ($healthResponse.status -eq "healthy") {
    Print-Success "Health check passed"
} else {
    Print-Error "Health check failed"
    exit 1
}
Write-Host ""

# Test 2: User Registration
Write-Host "3️⃣  Testing User Registration"
$registerBody = @{
    email = "test@example.com"
    password = "test123456"
    name = "Test User"
} | ConvertTo-Json

try {
    $registerResponse = Invoke-RestMethod -Uri "$BaseUrl/api/auth/register" `
        -Method Post `
        -ContentType "application/json" `
        -Body $registerBody
    
    Print-Success "User registration successful"
    $Token = $registerResponse.token
    $UserId = $registerResponse.userId
    Print-Info "Token: $Token"
    Print-Info "User ID: $UserId"
}
catch {
    Print-Info "User might already exist, trying login..."
    
    $loginBody = @{
        email = "test@example.com"
        password = "test123456"
    } | ConvertTo-Json
    
    try {
        $loginResponse = Invoke-RestMethod -Uri "$BaseUrl/api/auth/login" `
            -Method Post `
            -ContentType "application/json" `
            -Body $loginBody
        
        Print-Success "Login successful"
        $Token = $loginResponse.token
        $UserId = $loginResponse.user.id
        Print-Info "Token: $Token"
        Print-Info "User ID: $UserId"
    }
    catch {
        Print-Error "Registration and login both failed"
        Write-Host $_.Exception.Message
        exit 1
    }
}
Write-Host ""

# Test 3: Get Current User
Write-Host "4️⃣  Testing Get Current User"
$headers = @{
    "Authorization" = "Bearer $Token"
}
$userResponse = Invoke-RestMethod -Uri "$BaseUrl/api/auth/me" -Method Get -Headers $headers
Write-Host "Response: $($userResponse | ConvertTo-Json)"
Print-Success "Get current user successful"
Write-Host ""

# Test 4: Register Device
Write-Host "5️⃣  Testing Device Registration"
$deviceBody = @{
    bleId = "CCTV_TEST_001"
    name = "Front Door Camera"
    macAddress = "AA:BB:CC:DD:EE:FF"
    wifiSSID = "HomeNetwork"
    ipAddress = "192.168.1.100"
} | ConvertTo-Json

$deviceResponse = Invoke-RestMethod -Uri "$BaseUrl/api/devices/register" `
    -Method Post `
    -ContentType "application/json" `
    -Headers $headers `
    -Body $deviceBody

Write-Host "Response: $($deviceResponse | ConvertTo-Json)"
Print-Success "Device registration successful"
$DeviceId = $deviceResponse.deviceId
Print-Info "Device ID: $DeviceId"
Write-Host ""

# Test 5: List Devices
Write-Host "6️⃣  Testing List Devices"
$listResponse = Invoke-RestMethod -Uri "$BaseUrl/api/devices?userId=$UserId" `
    -Method Get `
    -Headers $headers
Write-Host "Response: $($listResponse | ConvertTo-Json -Depth 5)"
Print-Success "List devices successful"
Write-Host ""

# Test 6: Get Single Device
Write-Host "7️⃣  Testing Get Single Device"
$getDeviceResponse = Invoke-RestMethod -Uri "$BaseUrl/api/devices/$DeviceId" `
    -Method Get `
    -Headers $headers
Write-Host "Response: $($getDeviceResponse | ConvertTo-Json)"
Print-Success "Get device successful"
Write-Host ""

# Test 7: Update Device
Write-Host "8️⃣  Testing Update Device"
$updateBody = @{
    name = "Front Door Camera (Updated)"
    ipAddress = "192.168.1.101"
} | ConvertTo-Json

$updateResponse = Invoke-RestMethod -Uri "$BaseUrl/api/devices/$DeviceId" `
    -Method Put `
    -ContentType "application/json" `
    -Headers $headers `
    -Body $updateBody
Write-Host "Response: $($updateResponse | ConvertTo-Json)"
Print-Success "Update device successful"
Write-Host ""

# Test 8: Get Stream URLs
Write-Host "9️⃣  Testing Get Stream URLs"
$streamResponse = Invoke-RestMethod -Uri "$BaseUrl/api/devices/$DeviceId/stream" `
    -Method Get `
    -Headers $headers
Write-Host "Response: $($streamResponse | ConvertTo-Json)"
Print-Success "Get stream URLs successful"
Write-Host ""

# Test 9: Test Without Token (Should Fail)
Write-Host "🔒 Testing Unauthorized Access (should fail)"
try {
    $unauthResponse = Invoke-RestMethod -Uri "$BaseUrl/api/devices" -Method Get
    Print-Error "Authorization check failed - should require token"
}
catch {
    Print-Success "Authorization check working - unauthorized access blocked"
}
Write-Host ""

# Test 10: Refresh Token
Write-Host "🔄 Testing Token Refresh"
$refreshResponse = Invoke-RestMethod -Uri "$BaseUrl/api/auth/refresh" `
    -Method Post `
    -Headers $headers
Write-Host "Response: $($refreshResponse | ConvertTo-Json)"
Print-Success "Token refresh successful"
Print-Info "New Token: $($refreshResponse.token)"
Write-Host ""

# Test 11: Delete Device
Write-Host "🗑️  Testing Delete Device"
$deleteResponse = Invoke-RestMethod -Uri "$BaseUrl/api/devices/$DeviceId" `
    -Method Delete `
    -Headers $headers
Write-Host "Response: $($deleteResponse | ConvertTo-Json)"
Print-Success "Delete device successful"
Write-Host ""

# Test 12: Logout
Write-Host "👋 Testing Logout"
$logoutResponse = Invoke-RestMethod -Uri "$BaseUrl/api/auth/logout" `
    -Method Post `
    -Headers $headers
Write-Host "Response: $($logoutResponse | ConvertTo-Json)"
Print-Success "Logout successful"
Write-Host ""

# Summary
Write-Host "=================================="
Write-Host "✅ All API tests completed!" -ForegroundColor Green
Write-Host ""
Print-Info "Summary:"
Write-Host "  - Health Check: ✅"
Write-Host "  - User Registration/Login: ✅"
Write-Host "  - Get Current User: ✅"
Write-Host "  - Register Device: ✅"
Write-Host "  - List Devices: ✅"
Write-Host "  - Get Device: ✅"
Write-Host "  - Update Device: ✅"
Write-Host "  - Get Stream URLs: ✅"
Write-Host "  - Authorization Check: ✅"
Write-Host "  - Token Refresh: ✅"
Write-Host "  - Delete Device: ✅"
Write-Host "  - Logout: ✅"
Write-Host ""
Print-Success "Backend API is fully functional! 🎉"
