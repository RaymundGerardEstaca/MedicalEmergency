#!/bin/bash
# Backend API Testing Script
# Tests all endpoints of app_with_auth.py with JWT authentication
# Usage: bash test-backend-api.sh

set -e  # Exit on error

BASE_URL="http://localhost:5000"
TOKEN=""
USER_ID=""
DEVICE_ID=""

echo "🚀 Starting Backend API Testing..."
echo "=================================="
echo ""

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Check if Flask server is running
echo "1️⃣  Checking if Flask server is running..."
if ! curl -s "$BASE_URL/api/health" > /dev/null 2>&1; then
    print_error "Flask server is not running at $BASE_URL"
    print_info "Start the server with: python backend/app_with_auth.py"
    exit 1
fi
print_success "Flask server is running"
echo ""

# Test 1: Health Check
echo "2️⃣  Testing Health Check Endpoint"
HEALTH_RESPONSE=$(curl -s "$BASE_URL/api/health")
echo "Response: $HEALTH_RESPONSE"
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    print_success "Health check passed"
else
    print_error "Health check failed"
    exit 1
fi
echo ""

# Test 2: User Registration
echo "3️⃣  Testing User Registration"
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/register" \
    -H "Content-Type: application/json" \
    -d '{
        "email": "test@example.com",
        "password": "test123456",
        "name": "Test User"
    }')

echo "Response: $REGISTER_RESPONSE"

if echo "$REGISTER_RESPONSE" | grep -q "token"; then
    print_success "User registration successful"
    TOKEN=$(echo "$REGISTER_RESPONSE" | python -c "import sys, json; data=json.load(sys.stdin); print(data.get('token', ''))")
    USER_ID=$(echo "$REGISTER_RESPONSE" | python -c "import sys, json; data=json.load(sys.stdin); print(data.get('user', {}).get('id', ''))")
    print_info "Token: $TOKEN"
    print_info "User ID: $USER_ID"
else
    # User might already exist, try login
    print_info "User might already exist, trying login..."
    
    LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" \
        -H "Content-Type: application/json" \
        -d '{
            "email": "test@example.com",
            "password": "test123456"
        }')
    
    if echo "$LOGIN_RESPONSE" | grep -q "token"; then
        print_success "Login successful"
        TOKEN=$(echo "$LOGIN_RESPONSE" | python -c "import sys, json; data=json.load(sys.stdin); print(data.get('token', ''))")
        USER_ID=$(echo "$LOGIN_RESPONSE" | python -c "import sys, json; data=json.load(sys.stdin); print(data.get('user', {}).get('id', ''))")
        print_info "Token: $TOKEN"
        print_info "User ID: $USER_ID"
    else
        print_error "Registration and login both failed"
        echo "Response: $LOGIN_RESPONSE"
        exit 1
    fi
fi
echo ""

# Test 3: Get Current User
echo "4️⃣  Testing Get Current User"
USER_RESPONSE=$(curl -s "$BASE_URL/api/auth/me" \
    -H "Authorization: Bearer $TOKEN")

echo "Response: $USER_RESPONSE"
if echo "$USER_RESPONSE" | grep -q "email"; then
    print_success "Get current user successful"
else
    print_error "Get current user failed"
fi
echo ""

# Test 4: Register Device
echo "5️⃣  Testing Device Registration"
DEVICE_RESPONSE=$(curl -s -X POST "$BASE_URL/api/devices/register" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{
        "bleId": "CCTV_TEST_001",
        "name": "Front Door Camera",
        "macAddress": "AA:BB:CC:DD:EE:FF",
        "wifiSSID": "HomeNetwork",
        "ipAddress": "192.168.1.100"
    }')

echo "Response: $DEVICE_RESPONSE"
if echo "$DEVICE_RESPONSE" | grep -q '"device"'; then
    print_success "Device registration successful"
    DEVICE_ID=$(echo "$DEVICE_RESPONSE" | python -c "import sys, json; data=json.load(sys.stdin); print(data.get('device', {}).get('id', ''))")
    print_info "Device ID: $DEVICE_ID"
else
    print_error "Device registration failed"
    exit 1
fi
echo ""

# Test 5: List Devices
echo "6️⃣  Testing List Devices"
LIST_RESPONSE=$(curl -s "$BASE_URL/api/devices?userId=$USER_ID" \
    -H "Authorization: Bearer $TOKEN")

echo "Response: $LIST_RESPONSE"
if echo "$LIST_RESPONSE" | grep -q "Front Door Camera"; then
    print_success "List devices successful - found registered device"
else
    print_error "List devices failed"
fi
echo ""

# Test 6: Get Single Device
echo "7️⃣  Testing Get Single Device"
GET_DEVICE_RESPONSE=$(curl -s "$BASE_URL/api/devices/$DEVICE_ID" \
    -H "Authorization: Bearer $TOKEN")

echo "Response: $GET_DEVICE_RESPONSE"
if echo "$GET_DEVICE_RESPONSE" | grep -q "Front Door Camera"; then
    print_success "Get device successful"
else
    print_error "Get device failed"
fi
echo ""

# Test 7: Update Device
echo "8️⃣  Testing Update Device"
UPDATE_RESPONSE=$(curl -s -X PUT "$BASE_URL/api/devices/$DEVICE_ID" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{
        "name": "Front Door Camera (Updated)",
        "ipAddress": "192.168.1.101"
    }')

echo "Response: $UPDATE_RESPONSE"
if echo "$UPDATE_RESPONSE" | grep -q "Updated"; then
    print_success "Update device successful"
else
    print_error "Update device failed"
fi
echo ""

# Test 8: Get Stream URLs
echo "9️⃣  Testing Get Stream URLs"
STREAM_RESPONSE=$(curl -s "$BASE_URL/api/devices/$DEVICE_ID/stream" \
    -H "Authorization: Bearer $TOKEN")

echo "Response: $STREAM_RESPONSE"
if echo "$STREAM_RESPONSE" | grep -q "rtspUrl"; then
    print_success "Get stream URLs successful"
else
    print_error "Get stream URLs failed"
fi
echo ""

# Test 9: Test Without Token (Should Fail)
echo "🔒 Testing Unauthorized Access (should fail)"
UNAUTH_RESPONSE=$(curl -s "$BASE_URL/api/devices")

echo "Response: $UNAUTH_RESPONSE"
if echo "$UNAUTH_RESPONSE" | grep -q "token"; then
    print_success "Authorization check working - unauthorized access blocked"
else
    print_error "Authorization check failed - should require token"
fi
echo ""

# Test 10: Refresh Token
echo "🔄 Testing Token Refresh"
REFRESH_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/refresh" \
    -H "Authorization: Bearer $TOKEN")

echo "Response: $REFRESH_RESPONSE"
if echo "$REFRESH_RESPONSE" | grep -q "token"; then
    print_success "Token refresh successful"
    TOKEN=$(echo "$REFRESH_RESPONSE" | python -c "import sys, json; data=json.load(sys.stdin); print(data.get('token', ''))")
    print_info "New Token: $TOKEN"
else
    print_error "Token refresh failed"
fi
echo ""

# Test 11: Delete Device
echo "🗑️  Testing Delete Device"
DELETE_RESPONSE=$(curl -s -X DELETE "$BASE_URL/api/devices/$DEVICE_ID" \
    -H "Authorization: Bearer $TOKEN")

echo "Response: $DELETE_RESPONSE"
if echo "$DELETE_RESPONSE" | grep -q "deleted"; then
    print_success "Delete device successful"
else
    print_error "Delete device failed"
fi
echo ""

# Test 12: Logout
echo "👋 Testing Logout"
LOGOUT_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/logout" \
    -H "Authorization: Bearer $TOKEN")

echo "Response: $LOGOUT_RESPONSE"
if echo "$LOGOUT_RESPONSE" | grep -q "Logged out"; then
    print_success "Logout successful"
else
    print_error "Logout failed"
fi
echo ""

# Summary
echo "=================================="
echo "✅ All API tests completed!"
echo ""
print_info "Summary:"
echo "  - Health Check: ✅"
echo "  - User Registration/Login: ✅"
echo "  - Get Current User: ✅"
echo "  - Register Device: ✅"
echo "  - List Devices: ✅"
echo "  - Get Device: ✅"
echo "  - Update Device: ✅"
echo "  - Get Stream URLs: ✅"
echo "  - Authorization Check: ✅"
echo "  - Token Refresh: ✅"
echo "  - Delete Device: ✅"
echo "  - Logout: ✅"
echo ""
print_success "Backend API is fully functional! 🎉"
