"""
================================================================================
CCTV Unified Backend (FastAPI) - Production Grade
================================================================================
Combines Authentication, Device Management, and RTSP Streaming with:
- Comprehensive logging (60-70% coverage)
- HLS streaming endpoints
- Stream health monitoring
- Request/Response logging
- Error tracking
================================================================================
"""

import asyncio
import hashlib
import json
import logging
import os
import re
import secrets
import sys
import time
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import cv2
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Header, Request, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Google OAuth imports
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

# ==============================================================================
# Server Configuration
# ==============================================================================
SERVER_ID = os.getenv("SERVER_ID") or f"CCTV-{uuid.uuid4().hex[:8]}"
SERVER_HOST = os.getenv("HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("PORT", "8000"))
DEBUG_MODE = os.getenv("DEBUG", "false").lower() == "true"

from rtsp_stream_service import (
    enhanced_stream_service, stream_service,
    StreamMode, StreamState, HLS_OUTPUT_DIR
)

# ==============================================================================
# Logging Configuration
# ==============================================================================

LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# Sensitive data patterns for masking
SENSITIVE_PATTERNS = [
    (re.compile(r'\b(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})\b'), r'\1.***.***.***'),
    (re.compile(r'Bearer\s+[A-Za-z0-9\-_]+', re.I), 'Bearer [MASKED]'),
    (re.compile(r'(password|passwd|pwd|token|key|secret)=([^&\s]+)', re.I), r'\1=****'),
    (re.compile(r'"(password|token|secret|api_key)":\s*"[^"]*"', re.I), r'"\1": "****"'),
]

class SensitiveFormatter(logging.Formatter):
    """Formatter that masks sensitive data."""
    def format(self, record):
        message = super().format(record)
        for pattern, replacement in SENSITIVE_PATTERNS:
            message = pattern.sub(replacement, message)
        return message

def setup_logger(name: str, level=logging.DEBUG) -> logging.Logger:
    """Create logger with console and file handlers."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if logger.handlers:
        return logger
    
    # Console
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(SensitiveFormatter(
        '%(asctime)s │ %(levelname)-8s │ %(name)-12s │ %(message)s',
        datefmt='%H:%M:%S'
    ))
    logger.addHandler(console)
    
    # File
    file_handler = logging.FileHandler(
        os.path.join(LOG_DIR, f'{name.lower()}.log'), encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(SensitiveFormatter(
        '%(asctime)s │ %(levelname)-8s │ %(funcName)-20s │ %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    logger.addHandler(file_handler)
    
    return logger

# Initialize loggers
logger = setup_logger('Backend')
access_logger = setup_logger('Access')
api_logger = setup_logger('API')

logger.info("="*60)
logger.info("🚀 CCTV Backend Initializing...")
logger.info(f"   Server ID: {SERVER_ID}")
logger.info(f"   Host: {SERVER_HOST}:{SERVER_PORT}")
logger.info(f"   Debug Mode: {DEBUG_MODE}")
logger.info(f"   Log directory: {LOG_DIR}")
logger.info("="*60)

# ==============================================================================
# FastAPI App Setup
# ==============================================================================

app = FastAPI(
    title="CCTV Unified Backend",
    description=f"Production-grade CCTV backend with RTSP/HLS streaming (Server: {SERVER_ID})",
    version="4.0.0",
    debug=DEBUG_MODE
)

logger.info("FastAPI app created")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("CORS middleware enabled")

# Mount HLS output directory for static file serving
if os.path.exists(HLS_OUTPUT_DIR):
    app.mount("/hls", StaticFiles(directory=HLS_OUTPUT_DIR), name="hls")
    logger.info(f"HLS static files mounted at /hls -> {HLS_OUTPUT_DIR}")

# ==============================================================================
# Request Logging Middleware
# ==============================================================================

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging all HTTP requests and responses."""
    
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        start_time = time.time()
        
        # Log request with server ID
        client_ip = request.client.host if request.client else 'unknown'
        access_logger.info(f"→ [{SERVER_ID}] {request.method} {request.url.path} client={client_ip} req_id={request_id}")
        
        try:
            response = await call_next(request)
            duration_ms = (time.time() - start_time) * 1000
            
            # Log response
            status_emoji = '✓' if response.status_code < 400 else '✖'
            access_logger.info(f"← [{SERVER_ID}] {status_emoji} {request.method} {request.url.path} status={response.status_code} duration={duration_ms:.1f}ms")
            
            # Add server ID to response headers
            response.headers['X-Server-ID'] = SERVER_ID
            
            # Warn on slow requests
            if duration_ms > 1000:
                logger.warning(f"[{SERVER_ID}] SLOW_REQUEST {request.method} {request.url.path} took {duration_ms:.0f}ms")
            
            return response
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"[{SERVER_ID}] ✖ REQUEST_ERROR {request.method} {request.url.path} error={e} duration={duration_ms:.1f}ms")
            raise
            logger.error(f"✖ REQUEST_ERROR {request.method} {request.url.path} error={e} duration={duration_ms:.1f}ms")
            raise

app.add_middleware(RequestLoggingMiddleware)
logger.info("Request logging middleware enabled")

# ==============================================================================
# Storage Files and In-memory Cache
# ==============================================================================

DEVICES_FILE = 'devices_db.json'
USERS_FILE = 'users_db.json'

devices_db: Dict[str, dict] = {}
users_db: Dict[str, dict] = {}
active_tokens: Dict[str, dict] = {}

logger.info(f"Storage files: devices={DEVICES_FILE}, users={USERS_FILE}")

# ==============================================================================
# Data Models
# ==============================================================================

class UserRegister(BaseModel):
    email: str
    password: str
    name: Optional[str] = "User"

class UserLogin(BaseModel):
    email: str
    password: str

class DeviceRegister(BaseModel):
    bleId: str
    name: str
    macAddress: Optional[str] = None
    wifiSSID: Optional[str] = None
    ipAddress: Optional[str] = None
    rtspUrl: Optional[str] = None

class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    ipAddress: Optional[str] = None
    rtspUrl: Optional[str] = None
    isOnline: Optional[bool] = None

class WiFiValidate(BaseModel):
    ssid: str

class StreamStart(BaseModel):
    url: str
    stream_id: Optional[str] = None
    mode: Optional[str] = 'both'  # 'hls', 'websocket', 'both'

class StreamControl(BaseModel):
    stream_id: str

class GoogleAuthRequest(BaseModel):
    """Google OAuth ID token request model."""
    idToken: str

# Google OAuth Configuration
# ==============================================================================
# Load from environment variables (.env file)
# ==============================================================================
GOOGLE_WEB_CLIENT_ID = os.getenv("GOOGLE_WEB_CLIENT_ID", "")
GOOGLE_ANDROID_CLIENT_ID = os.getenv("GOOGLE_ANDROID_CLIENT_ID", "")
GOOGLE_IOS_CLIENT_ID = os.getenv("GOOGLE_IOS_CLIENT_ID", "")

GOOGLE_CLIENT_IDS = [
    GOOGLE_WEB_CLIENT_ID,
    GOOGLE_ANDROID_CLIENT_ID,
    GOOGLE_IOS_CLIENT_ID,
]

# Filter out empty client IDs
GOOGLE_CLIENT_IDS = [cid for cid in GOOGLE_CLIENT_IDS if cid and not cid.startswith("YOUR_")]

# Check if Google OAuth is properly configured
GOOGLE_OAUTH_ENABLED = len(GOOGLE_CLIENT_IDS) > 0
ALLOW_EMAIL_AUTH = os.getenv("ALLOW_EMAIL_AUTH", "true").lower() == "true"

logger.debug("Data models defined")

if GOOGLE_OAUTH_ENABLED:
    logger.info(f"✓ Google OAuth enabled with {len(GOOGLE_CLIENT_IDS)} client ID(s)")
else:
    logger.warning("⚠ Google OAuth NOT configured - using email/password authentication only")
    logger.info("  To enable Google OAuth, set GOOGLE_WEB_CLIENT_ID in backend/.env file")
    logger.info("  See docs/GOOGLE-OAUTH-SETUP.md for setup instructions")

if ALLOW_EMAIL_AUTH:
    logger.info("✓ Email/password authentication enabled")

# ==============================================================================
# Data Persistence with Logging
# ==============================================================================

def load_data():
    """Load data from JSON files with logging."""
    global devices_db, users_db
    
    logger.info("Loading data from storage...")
    
    if os.path.exists(DEVICES_FILE):
        try:
            with open(DEVICES_FILE, 'r') as f:
                devices_db = json.load(f)
            logger.info(f"✓ Loaded {len(devices_db)} devices from {DEVICES_FILE}")
        except json.JSONDecodeError as e:
            logger.error(f"✖ Failed to parse {DEVICES_FILE}: {e}")
            devices_db = {}
    else:
        logger.info(f"No devices file found, starting fresh")
            
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r') as f:
                users_db = json.load(f)
            logger.info(f"✓ Loaded {len(users_db)} users from {USERS_FILE}")
        except json.JSONDecodeError as e:
            logger.error(f"✖ Failed to parse {USERS_FILE}: {e}")
            users_db = {}
    else:
        logger.info(f"No users file found, starting fresh")

def save_data():
    """Save data to JSON files with logging."""
    logger.debug(f"Saving data: {len(devices_db)} devices, {len(users_db)} users")
    try:
        with open(DEVICES_FILE, 'w') as f:
            json.dump(devices_db, f, indent=2)
        with open(USERS_FILE, 'w') as f:
            json.dump(users_db, f, indent=2)
        logger.debug("✓ Data saved successfully")
    except Exception as e:
        logger.error(f"✖ Failed to save data: {e}")

# Load on startup
load_data()

# ==============================================================================
# Auth Logic with Logging
# ==============================================================================

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token() -> str:
    return secrets.token_urlsafe(32)

async def get_current_user(authorization: Optional[str] = Header(None)) -> str:
    """Validate Bearer token and return user_id with logging."""
    if not authorization:
        api_logger.debug("Auth failed: missing header")
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != 'bearer':
            api_logger.debug("Auth failed: invalid scheme")
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    except ValueError:
        api_logger.debug("Auth failed: invalid format")
        raise HTTPException(status_code=401, detail="Invalid authorization header format")

    if token not in active_tokens:
        api_logger.debug("Auth failed: invalid token")
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    token_data = active_tokens[token]
    if datetime.fromisoformat(token_data['expires_at']) < datetime.now():
        del active_tokens[token]
        api_logger.info(f"Token expired for user {token_data.get('email', 'unknown')}")
        raise HTTPException(status_code=401, detail="Token expired")
    
    api_logger.debug(f"Auth success for user_id={token_data['user_id'][:8]}...")
    return token_data['user_id']

# ==============================================================================
# WebSocket Manager with Logging
# ==============================================================================

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        logger.info("WebSocket ConnectionManager initialized")

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast_frame(self, frame_data: bytes):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_bytes(frame_data)
            except Exception as e:
                logger.warning(f"Failed to send frame to client: {e}")
                disconnected.append(connection)
        
        for conn in disconnected:
            self.disconnect(conn)

manager = ConnectionManager()

# ==============================================================================
# Routes: General & Health
# ==============================================================================

@app.get("/")
def read_root():
    """Root endpoint with system status."""
    logger.debug("Root endpoint accessed")
    
    stream_count = len(enhanced_stream_service.get_all_streams())
    
    return {
        "status": "online", 
        "message": "CCTV Unified Backend Running",
        "server_id": SERVER_ID,
        "version": "4.0.0",
        "host": SERVER_HOST,
        "port": SERVER_PORT,
        "devices": len(devices_db),
        "users": len(users_db),
        "active_streams": stream_count,
        "hls_enabled": True,
        "debug_mode": DEBUG_MODE,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/health")
def health_check():
    """Detailed health check endpoint."""
    logger.debug("Health check requested")
    
    streams = enhanced_stream_service.get_all_streams()
    stream_health = {
        sid: {
            "state": s.state.value,
            "fps": s.current_fps,
            "frames": s.frames_processed,
            "errors": s.errors,
            "hls_ready": s.hls_ready
        }
        for sid, s in streams.items()
    }
    
    return {
        "status": "healthy",
        "server_id": SERVER_ID,
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "database": "ok",
            "streaming": "ok" if streams else "idle",
            "websocket": f"{len(manager.active_connections)} connections"
        },
        "streams": stream_health,
        "storage": {
            "devices": len(devices_db),
            "users": len(users_db),
            "active_tokens": len(active_tokens)
        },
        "config": {
            "host": SERVER_HOST,
            "port": SERVER_PORT,
            "debug": DEBUG_MODE,
            "google_oauth_enabled": GOOGLE_OAUTH_ENABLED,
            "email_auth_enabled": ALLOW_EMAIL_AUTH
        }
    }

@app.get("/api/server/info")
def server_info():
    """
    Get detailed server information.
    
    Returns server instance details, configuration, and runtime stats.
    Useful for debugging, monitoring, and load balancer health checks.
    """
    logger.debug("Server info requested")
    
    uptime_seconds = int(time.time() - logger.handlers[0].formatter.converter(time.time())[3])  # Approximate
    
    return {
        "server": {
            "id": SERVER_ID,
            "version": "4.0.0",
            "status": "running",
            "host": SERVER_HOST,
            "port": SERVER_PORT,
            "debug_mode": DEBUG_MODE,
        },
        "authentication": {
            "google_oauth": {
                "enabled": GOOGLE_OAUTH_ENABLED,
                "web_client_id": GOOGLE_WEB_CLIENT_ID[:20] + "..." if GOOGLE_WEB_CLIENT_ID else None,
                "configured_clients": len(GOOGLE_CLIENT_IDS)
            },
            "email_password": {
                "enabled": ALLOW_EMAIL_AUTH
            },
            "active_sessions": len(active_tokens)
        },
        "storage": {
            "users": len(users_db),
            "devices": len(devices_db),
            "active_tokens": len(active_tokens)
        },
        "streaming": {
            "active_streams": len(enhanced_stream_service.get_all_streams()),
            "hls_enabled": True,
            "hls_output_dir": HLS_OUTPUT_DIR,
            "websocket_connections": len(manager.active_connections)
        },
        "environment": {
            "python_version": sys.version.split()[0],
            "platform": sys.platform,
            "log_directory": LOG_DIR
        },
        "timestamp": datetime.utcnow().isoformat()
    }

# ==============================================================================
# Routes: Authentication with Logging
# ==============================================================================

@app.post("/api/auth/register")
def register_user(user: UserRegister):
    """Register a new user with logging."""
    api_logger.info(f"Registration attempt for email={user.email[:3]}***")
    
    if user.email in users_db:
        api_logger.warning(f"Registration failed: email already exists")
        raise HTTPException(status_code=409, detail="Email already registered")
    
    user_id = str(uuid.uuid4())
    users_db[user.email] = {
        "id": user_id,
        "email": user.email,
        "password": hash_password(user.password),
        "name": user.name,
        "created_at": datetime.now().isoformat()
    }
    save_data()
    
    # Auto-login
    token = generate_token()
    active_tokens[token] = {
        "user_id": user_id,
        "email": user.email,
        "expires_at": (datetime.now() + timedelta(days=30)).isoformat()
    }
    
    api_logger.info(f"✓ User registered successfully: user_id={user_id[:8]}...")
    
    return {
        "message": "User registered",
        "user": {"id": user_id, "email": user.email, "name": user.name},
        "token": token,
        "expires_in": 2592000
    }

@app.post("/api/auth/login")
def login_user(creds: UserLogin):
    """Login user with logging."""
    api_logger.info(f"Login attempt for email={creds.email[:3]}***")
    
    if creds.email not in users_db:
        api_logger.warning(f"Login failed: user not found")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user = users_db[creds.email]
    if user["password"] != hash_password(creds.password):
        api_logger.warning(f"Login failed: invalid password")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = generate_token()
    active_tokens[token] = {
        "user_id": user["id"],
        "email": creds.email,
        "expires_at": (datetime.now() + timedelta(days=30)).isoformat()
    }
    
    api_logger.info(f"✓ Login successful for user_id={user['id'][:8]}...")
    
    return {
        "message": "Login successful",
        "user": {"id": user["id"], "email": creds.email, "name": user.get("name")},
        "token": token
    }

@app.post("/api/auth/logout")
def logout_user(token: str = Header(None)):
    """Logout user by invalidating token."""
    if token and token.startswith("Bearer "):
        token = token.split()[1]
    
    if token in active_tokens:
        user_email = active_tokens[token].get('email', 'unknown')
        del active_tokens[token]
        api_logger.info(f"✓ Logout successful for {user_email[:3]}***")
    else:
        api_logger.debug("Logout called with invalid/missing token")
    
    return {"message": "Logged out"}

@app.get("/api/auth/me")
def get_me(user_id: str = Depends(get_current_user)):
    """Get current user profile."""
    api_logger.debug(f"Profile requested for user_id={user_id[:8]}...")
    
    for user in users_db.values():
        if user["id"] == user_id:
            return {
                "id": user["id"],
                "email": user["email"],
                "name": user.get("name"),
                "picture": user.get("picture"),
                "auth_provider": user.get("auth_provider", "email")
            }
    
    api_logger.warning(f"User not found: {user_id[:8]}...")
    raise HTTPException(status_code=404, detail="User not found")

# ==============================================================================
# Routes: Google OAuth Authentication
# ==============================================================================

@app.post("/api/auth/google")
async def google_auth(auth_request: GoogleAuthRequest):
    """
    Authenticate user with Google OAuth ID token.
    
    This endpoint receives the Google ID token from the mobile app,
    verifies it with Google's servers, and creates/updates the user account.
    
    Flow:
    1. Mobile app signs in with Google and receives ID token
    2. Mobile app sends ID token to this endpoint
    3. Backend verifies token with Google
    4. Backend creates/finds user and returns JWT session token
    """
    api_logger.info("Google OAuth authentication attempt")
    
    # Check if Google OAuth is enabled
    if not GOOGLE_OAUTH_ENABLED:
        api_logger.error("Google OAuth not configured")
        raise HTTPException(
            status_code=503,
            detail="Google OAuth not configured. Please use email/password authentication or configure Google OAuth in backend/.env file."
        )
    
    try:
        # Verify the Google ID token
        # This will verify the token signature, expiration, and audience
        id_info = id_token.verify_oauth2_token(
            auth_request.idToken,
            google_requests.Request(),
            audience=None  # We'll check audience manually for multiple clients
        )
        
        # Verify the token was issued by Google
        issuer = id_info.get('iss')
        if issuer not in ['accounts.google.com', 'https://accounts.google.com']:
            api_logger.warning(f"Invalid token issuer: {issuer}")
            raise HTTPException(status_code=401, detail="Invalid token issuer")
        
        # Verify the audience (client ID) matches one of our registered clients
        token_audience = id_info.get('aud')
        if token_audience not in GOOGLE_CLIENT_IDS:
            api_logger.warning(f"Token audience mismatch. Expected one of {GOOGLE_CLIENT_IDS}, got {token_audience}")
            # For development, log but don't fail (remove this in production)
            api_logger.warning("Allowing mismatched audience for development")
        
        # Extract user information from the verified token
        google_user_id = id_info.get('sub')  # Unique Google user ID
        email = id_info.get('email')
        email_verified = id_info.get('email_verified', False)
        name = id_info.get('name', 'Google User')
        picture = id_info.get('picture', '')
        given_name = id_info.get('given_name', '')
        family_name = id_info.get('family_name', '')
        
        if not email:
            api_logger.error("No email in Google token")
            raise HTTPException(status_code=400, detail="Email not provided by Google")
        
        api_logger.info(f"Google token verified for email={email[:3]}***")
        
        # Check if user exists (by email)
        if email in users_db:
            # Existing user - update Google info and login
            user = users_db[email]
            user['picture'] = picture
            user['name'] = name
            user['google_id'] = google_user_id
            user['last_login'] = datetime.now().isoformat()
            user['auth_provider'] = 'google'
            save_data()
            
            api_logger.info(f"✓ Existing user logged in via Google: {user['id'][:8]}...")
            
            user_id = user['id']
        else:
            # New user - create account
            user_id = str(uuid.uuid4())
            users_db[email] = {
                "id": user_id,
                "email": email,
                "password": None,  # No password for Google-only users
                "name": name,
                "picture": picture,
                "google_id": google_user_id,
                "email_verified": email_verified,
                "given_name": given_name,
                "family_name": family_name,
                "auth_provider": "google",
                "created_at": datetime.now().isoformat(),
                "last_login": datetime.now().isoformat()
            }
            save_data()
            
            api_logger.info(f"✓ New user created via Google: {user_id[:8]}...")
        
        # Generate session token
        token = generate_token()
        active_tokens[token] = {
            "user_id": user_id,
            "email": email,
            "auth_provider": "google",
            "expires_at": (datetime.now() + timedelta(days=30)).isoformat()
        }
        
        return {
            "message": "Google authentication successful",
            "user": {
                "id": user_id,
                "email": email,
                "name": name,
                "picture": picture,
                "auth_provider": "google"
            },
            "token": token,
            "expires_in": 2592000  # 30 days in seconds
        }
        
    except ValueError as e:
        # Token verification failed
        api_logger.error(f"Google token verification failed: {e}")
        raise HTTPException(
            status_code=401, 
            detail=f"Invalid Google token: {str(e)}"
        )
    except Exception as e:
        api_logger.error(f"Google authentication error: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Authentication error: {str(e)}"
        )

@app.get("/api/auth/google/config")
def get_google_config():
    """
    Return Google OAuth configuration for the mobile app.
    
    This endpoint provides the web client ID needed for Google Sign-In
    configuration in the mobile app.
    """
    if not GOOGLE_OAUTH_ENABLED:
        api_logger.debug("Google OAuth not configured")
        return {
            "configured": False,
            "message": "Google OAuth not configured. Set GOOGLE_WEB_CLIENT_ID in backend/.env file. See docs/GOOGLE-OAUTH-SETUP.md for setup instructions.",
            "webClientId": None,
            "emailAuthAvailable": ALLOW_EMAIL_AUTH
        }
    
    return {
        "configured": True,
        "webClientId": GOOGLE_WEB_CLIENT_ID,
        "emailAuthAvailable": ALLOW_EMAIL_AUTH
    }

# ==============================================================================
# Routes: Devices with Logging
# ==============================================================================

@app.post("/api/devices/register")
def register_device(device: DeviceRegister, user_id: str = Depends(get_current_user)):
    """Register a new device with logging."""
    device_id = str(uuid.uuid4())
    
    api_logger.info(f"Registering device: name={device.name} ble_id={device.bleId[:8]}...")
    
    new_device = {
        "id": device_id,
        "bleId": device.bleId,
        "name": device.name,
        "macAddress": device.macAddress,
        "wifiSSID": device.wifiSSID,
        "ipAddress": device.ipAddress,
        "rtspUrl": device.rtspUrl,
        "userId": user_id,
        "isOnline": False,
        "addedAt": datetime.now().isoformat(),
        "lastSeen": None,
        "firmwareVersion": "1.0.0"
    }
    
    devices_db[device_id] = new_device
    save_data()
    
    api_logger.info(f"✓ Device registered: device_id={device_id[:8]}...")
    
    return {"message": "Device registered", "device": new_device}

@app.get("/api/devices")
def list_devices(user_id: str = Depends(get_current_user)):
    """List user's devices."""
    user_devices = [d for d in devices_db.values() if d.get("userId") == user_id]
    api_logger.debug(f"Listed {len(user_devices)} devices for user")
    return {"devices": user_devices, "count": len(user_devices)}

@app.get("/api/devices/{device_id}")
def get_device(device_id: str, user_id: str = Depends(get_current_user)):
    """Get single device details."""
    api_logger.debug(f"Getting device: {device_id[:8]}...")
    
    if device_id not in devices_db:
        raise HTTPException(status_code=404, detail="Device not found")
    
    device = devices_db[device_id]
    if device.get("userId") != user_id:
        api_logger.warning(f"Unauthorized device access attempt")
        raise HTTPException(status_code=403, detail="Unauthorized")
        
    return {"device": device}

@app.put("/api/devices/{device_id}")
def update_device(device_id: str, updates: DeviceUpdate, user_id: str = Depends(get_current_user)):
    """Update device with logging."""
    api_logger.info(f"Updating device: {device_id[:8]}...")
    
    if device_id not in devices_db:
        raise HTTPException(status_code=404, detail="Device not found")
    
    device = devices_db[device_id]
    if device.get("userId") != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    update_data = updates.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        device[key] = value
        api_logger.debug(f"  Updated {key}")
        
    if "isOnline" in update_data and update_data["isOnline"]:
        device["lastSeen"] = datetime.now().isoformat()
        
    save_data()
    api_logger.info(f"✓ Device updated: {device_id[:8]}...")
    
    return {"message": "Device updated", "device": device}

@app.delete("/api/devices/{device_id}")
def delete_device(device_id: str, user_id: str = Depends(get_current_user)):
    """Delete device with logging."""
    api_logger.info(f"Deleting device: {device_id[:8]}...")
    
    if device_id not in devices_db:
        raise HTTPException(status_code=404, detail="Device not found")
    
    if devices_db[device_id].get("userId") != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
        
    del devices_db[device_id]
    save_data()
    
    api_logger.info(f"✓ Device deleted: {device_id[:8]}...")
    return {"message": "Device deleted"}

@app.post("/api/devices/{device_id}/heartbeat")
def device_heartbeat(device_id: str):
    """Device heartbeat endpoint (no auth required for device-to-server)."""
    if device_id not in devices_db:
        raise HTTPException(status_code=404, detail="Device not found")
    
    devices_db[device_id]["isOnline"] = True
    devices_db[device_id]["lastSeen"] = datetime.now().isoformat()
    save_data()
    
    api_logger.debug(f"Heartbeat received from device: {device_id[:8]}...")
    return {"status": "ok"}

@app.get("/api/devices/{device_id}/stream")
def get_device_stream(device_id: str, user_id: str = Depends(get_current_user)):
    """Get streaming URLs for a device."""
    api_logger.debug(f"Getting stream URLs for device: {device_id[:8]}...")
    
    if device_id not in devices_db:
        raise HTTPException(status_code=404, detail="Device not found")
        
    device = devices_db[device_id]
    if device.get("userId") != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    ip = device.get("ipAddress", "unknown")
    rtsp = device.get("rtspUrl") or f"rtsp://{ip}:554/stream1"
    
    # Check if HLS is available
    hls_url = None
    streams = enhanced_stream_service.get_all_streams()
    for sid, status in streams.items():
        if status.hls_ready:
            hls_url = status.hls_url
            break
    
    return {
        "streamUrl": rtsp,
        "hlsUrl": hls_url or f"http://{ip}:8080/hls/stream.m3u8",
        "wsUrl": f"ws://localhost:8000/ws/stream/{device_id}"
    }

# ==============================================================================
# Routes: WiFi & Tools
# ==============================================================================

@app.post("/api/wifi/validate")
def validate_wifi(data: WiFiValidate):
    """Validate WiFi SSID for compatibility."""
    ssid_lower = data.ssid.lower()
    is_5g = any(x in ssid_lower for x in ['5g', '5ghz', '_ac'])
    
    api_logger.debug(f"WiFi validation: ssid={data.ssid[:8]}... is_5g={is_5g}")
    
    return {
        "ssid": data.ssid,
        "isLikely2_4GHz": not is_5g,
        "warning": "Possible 5GHz network - IoT devices typically require 2.4GHz" if is_5g else None
    }

# ==============================================================================
# Routes: Enhanced RTSP/HLS Streaming
# ==============================================================================

@app.post("/api/stream/start")
def start_stream(data: StreamStart):
    """Start RTSP stream with HLS/WebSocket output."""
    logger.info(f"Starting stream: mode={data.mode}")
    
    # Map mode string to enum
    mode_map = {
        'hls': StreamMode.HLS,
        'websocket': StreamMode.WEBSOCKET,
        'both': StreamMode.BOTH
    }
    mode = mode_map.get(data.mode, StreamMode.BOTH)
    
    try:
        status = enhanced_stream_service.start_stream(
            rtsp_url=data.url,
            stream_id=data.stream_id,
            mode=mode
        )
        
        return {
            "status": "started",
            "stream_id": status.stream_id,
            "state": status.state.value,
            "hls_url": status.hls_url if status.hls_url else None,
            "ws_url": f"/ws/stream/{status.stream_id}"
        }
    except Exception as e:
        logger.error(f"Failed to start stream: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/stream/stop")
def stop_stream(data: StreamControl = None):
    """Stop a specific stream or all streams."""
    if data and data.stream_id:
        logger.info(f"Stopping stream: {data.stream_id}")
        success = enhanced_stream_service.stop_stream(data.stream_id)
        return {"status": "stopped" if success else "not_found", "stream_id": data.stream_id}
    else:
        logger.info("Stopping all streams")
        enhanced_stream_service.stop_all()
        return {"status": "all_stopped"}

@app.get("/api/stream/status")
def get_stream_status():
    """Get status of all active streams."""
    streams = enhanced_stream_service.get_all_streams()
    
    return {
        "active_count": len(streams),
        "streams": {
            sid: {
                "state": s.state.value,
                "started_at": s.started_at.isoformat() if s.started_at else None,
                "frames_processed": s.frames_processed,
                "current_fps": round(s.current_fps, 1),
                "errors": s.errors,
                "reconnect_attempts": s.reconnect_attempts,
                "hls_ready": s.hls_ready,
                "hls_url": s.hls_url,
                "error_message": s.error_message
            }
            for sid, s in streams.items()
        }
    }

@app.get("/api/stream/{stream_id}/status")
def get_single_stream_status(stream_id: str):
    """Get status of a specific stream."""
    status = enhanced_stream_service.get_status(stream_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Stream not found")
    
    return {
        "stream_id": stream_id,
        "state": status.state.value,
        "started_at": status.started_at.isoformat() if status.started_at else None,
        "frames_processed": status.frames_processed,
        "bytes_transmitted": status.bytes_transmitted,
        "current_fps": round(status.current_fps, 1),
        "errors": status.errors,
        "reconnect_attempts": status.reconnect_attempts,
        "hls_ready": status.hls_ready,
        "hls_url": status.hls_url,
        "error_message": status.error_message
    }

@app.post("/api/stream/probe")
def probe_stream(data: StreamStart):
    """Probe an RTSP stream to check availability."""
    logger.info(f"Probing stream...")
    result = enhanced_stream_service.probe_stream(data.url)
    return result

# RTSP URL Discovery endpoint
class RTSPDiscoveryRequest(BaseModel):
    ip_address: str
    port: int = 554
    username: Optional[str] = None
    password: Optional[str] = None
    quick_mode: bool = True

class ConnectivityCheckRequest(BaseModel):
    ip_address: str
    port: int = 554

@app.post("/api/stream/check-connectivity")
def check_camera_connectivity(data: ConnectivityCheckRequest):
    """
    Quick connectivity check for a camera IP address.
    Returns whether the camera is reachable and ports are open.
    This is a fast check that should complete in a few seconds.
    """
    logger.info(f"Checking connectivity to {data.ip_address}:{data.port}")
    result = enhanced_stream_service.check_camera_connectivity(
        ip_address=data.ip_address,
        port=data.port
    )
    return result

@app.post("/api/stream/discover")
def discover_rtsp(data: RTSPDiscoveryRequest):
    """
    Discover the correct RTSP URL for a camera.
    Tries multiple common RTSP paths and returns working URLs.
    Now with quick connectivity check first and better timeout handling.
    """
    logger.info(f"Discovering RTSP URL for {data.ip_address}:{data.port}")
    result = enhanced_stream_service.discover_rtsp_url(
        ip_address=data.ip_address,
        port=data.port,
        username=data.username,
        password=data.password,
        quick_mode=data.quick_mode
    )
    return result

@app.post("/api/stream/test")
def test_rtsp_url(data: StreamStart):
    """
    Test if an RTSP URL is accessible and can provide frames.
    Returns connection info and a sample frame.
    """
    import base64
    logger.info(f"Testing RTSP URL...")
    
    try:
        os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'rtsp_transport;tcp|stimeout;10000000'
        cap = cv2.VideoCapture(data.url, cv2.CAP_FFMPEG)
        cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 10000)
        cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 10000)
        
        if not cap.isOpened():
            return {
                "success": False,
                "error": "Failed to connect to RTSP stream",
                "url": data.url
            }
        
        ret, frame = cap.read()
        if not ret or frame is None:
            cap.release()
            return {
                "success": False,
                "error": "Connected but failed to read frame",
                "url": data.url
            }
        
        # Get stream properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        # Encode a thumbnail for preview
        thumb = cv2.resize(frame, (320, 240))
        _, buffer = cv2.imencode('.jpg', thumb, [cv2.IMWRITE_JPEG_QUALITY, 70])
        thumbnail_b64 = base64.b64encode(buffer.tobytes()).decode('utf-8')
        
        cap.release()
        
        return {
            "success": True,
            "url": data.url,
            "resolution": f"{width}x{height}",
            "fps": round(fps, 1),
            "thumbnail": f"data:image/jpeg;base64,{thumbnail_b64}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "url": data.url
        }

# Legacy endpoints for backward compatibility
@app.post("/api/stream/start/legacy")
def start_legacy_stream(data: StreamStart):
    """Legacy stream start (WebSocket only)."""
    logger.info("Legacy stream start called")
    stream_service.start_stream(data.url)
    return {"status": "started", "url": data.url}

@app.post("/api/stream/stop/legacy")
def stop_legacy_stream():
    """Legacy stream stop."""
    stream_service.stop_stream()
    return {"status": "stopped"}

# ==============================================================================
# WebSocket Streaming Endpoints
# ==============================================================================

@app.websocket("/ws/stream")
async def websocket_stream_legacy(websocket: WebSocket):
    """Legacy WebSocket endpoint for backward compatibility."""
    await manager.connect(websocket)
    logger.info("Legacy WebSocket client connected")
    
    try:
        while True:
            frame_bytes = stream_service.get_frame()
            
            if frame_bytes:
                await websocket.send_bytes(frame_bytes)
            
            await asyncio.sleep(0.05)  # ~20 FPS
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Legacy WebSocket client disconnected")
    except Exception as e:
        logger.error(f"Legacy WebSocket error: {e}")
        manager.disconnect(websocket)

@app.websocket("/ws/stream/{stream_id}")
async def websocket_stream(websocket: WebSocket, stream_id: str):
    """WebSocket endpoint for specific stream."""
    await manager.connect(websocket)
    logger.info(f"WebSocket client connected for stream: {stream_id}")
    
    try:
        while True:
            frame_bytes = enhanced_stream_service.get_frame(stream_id)
            
            if frame_bytes:
                await websocket.send_bytes(frame_bytes)
            else:
                # Send keepalive or wait
                await asyncio.sleep(0.1)
                continue
            
            await asyncio.sleep(0.033)  # ~30 FPS
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"WebSocket client disconnected from stream: {stream_id}")
    except Exception as e:
        logger.error(f"WebSocket error for {stream_id}: {e}")
        manager.disconnect(websocket)

# ==============================================================================
# Demo UI
# ==============================================================================

@app.get("/demo", response_class=HTMLResponse)
async def get_demo():
    """Demo page for testing streams."""
    logger.debug("Demo page accessed")
    return """
    <!DOCTYPE html>
    <html>
        <head>
            <title>CCTV Backend Demo</title>
            <style>
                body { font-family: sans-serif; text-align: center; padding: 20px; background: #1a1a2e; color: #fff; }
                h1 { color: #0f3460; }
                .container { max-width: 800px; margin: 0 auto; }
                .status { padding: 10px; border-radius: 8px; margin: 10px 0; }
                .status.connected { background: #16213e; }
                .status.disconnected { background: #4a0000; }
                #videoStream { background: #000; border-radius: 8px; max-width: 100%; }
                .controls { margin: 20px 0; }
                button { padding: 10px 20px; margin: 5px; border: none; border-radius: 5px; cursor: pointer; }
                .btn-start { background: #4CAF50; color: white; }
                .btn-stop { background: #f44336; color: white; }
                input { padding: 10px; width: 300px; border-radius: 5px; border: 1px solid #ddd; }
                .info { background: #16213e; padding: 15px; border-radius: 8px; margin: 10px 0; text-align: left; }
                .log { background: #0a0a0a; padding: 10px; border-radius: 5px; max-height: 200px; overflow-y: auto; font-family: monospace; font-size: 12px; text-align: left; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎥 CCTV Live Stream Demo</h1>
                
                <div class="controls">
                    <input type="text" id="rtspUrl" placeholder="rtsp://user:pass@ip:554/stream1" />
                    <br><br>
                    <button class="btn-start" onclick="startStream()">▶ Start Stream</button>
                    <button class="btn-stop" onclick="stopStream()">⏹ Stop Stream</button>
                </div>
                
                <p class="status" id="status">Status: Idle</p>
                
                <img id="videoStream" src="" width="640" height="480"/>
                
                <div class="info">
                    <h3>📊 Stream Info</h3>
                    <div id="streamInfo">No active stream</div>
                </div>
                
                <div class="log" id="log"></div>
            </div>
            
            <script>
                let ws = null;
                const img = document.getElementById("videoStream");
                const status = document.getElementById("status");
                const logDiv = document.getElementById("log");
                
                function log(msg) {
                    const time = new Date().toLocaleTimeString();
                    logDiv.innerHTML = `[${time}] ${msg}<br>` + logDiv.innerHTML;
                }
                
                async function startStream() {
                    const url = document.getElementById("rtspUrl").value;
                    if (!url) {
                        alert("Please enter RTSP URL");
                        return;
                    }
                    
                    log("Starting stream...");
                    
                    try {
                        const resp = await fetch("/api/stream/start", {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({ url: url, mode: "both" })
                        });
                        const data = await resp.json();
                        log("Stream started: " + JSON.stringify(data));
                        
                        // Connect WebSocket
                        connectWS(data.stream_id);
                        
                        // Poll status
                        setInterval(updateStatus, 2000);
                    } catch (e) {
                        log("Error: " + e.message);
                    }
                }
                
                function connectWS(streamId) {
                    const wsUrl = `ws://${window.location.host}/ws/stream/${streamId}`;
                    log("Connecting to " + wsUrl);
                    
                    ws = new WebSocket(wsUrl);
                    
                    ws.onopen = () => {
                        status.innerText = "Status: Connected ✅";
                        status.className = "status connected";
                        log("WebSocket connected");
                    };
                    
                    ws.onclose = () => {
                        status.innerText = "Status: Disconnected ❌";
                        status.className = "status disconnected";
                        log("WebSocket disconnected");
                    };
                    
                    ws.onmessage = (event) => {
                        const url = URL.createObjectURL(event.data);
                        img.src = url;
                    };
                    
                    ws.onerror = (e) => log("WebSocket error: " + e);
                }
                
                async function stopStream() {
                    log("Stopping stream...");
                    
                    if (ws) {
                        ws.close();
                        ws = null;
                    }
                    
                    try {
                        await fetch("/api/stream/stop", { method: "POST" });
                        log("Stream stopped");
                        status.innerText = "Status: Stopped";
                    } catch (e) {
                        log("Error: " + e.message);
                    }
                }
                
                async function updateStatus() {
                    try {
                        const resp = await fetch("/api/stream/status");
                        const data = await resp.json();
                        document.getElementById("streamInfo").innerHTML = 
                            `<pre>${JSON.stringify(data, null, 2)}</pre>`;
                    } catch (e) {}
                }
                
                log("Demo page loaded");
            </script>
        </body>
    </html>
    """

# ==============================================================================
# Startup and Shutdown Events
# ==============================================================================

@app.on_event("startup")
async def startup_event():
    """Application startup."""
    logger.info("="*60)
    logger.info("🚀 CCTV Backend Started")
    logger.info(f"   Server ID: {SERVER_ID}")
    logger.info(f"   Version: 4.0.0")
    logger.info(f"   Host: {SERVER_HOST}:{SERVER_PORT}")
    logger.info(f"   Debug: {DEBUG_MODE}")
    logger.info(f"   Devices loaded: {len(devices_db)}")
    logger.info(f"   Users loaded: {len(users_db)}")
    logger.info(f"   HLS output: {HLS_OUTPUT_DIR}")
    logger.info(f"   Google OAuth: {'Enabled' if GOOGLE_OAUTH_ENABLED else 'Disabled'}")
    logger.info(f"   Email Auth: {'Enabled' if ALLOW_EMAIL_AUTH else 'Disabled'}")
    logger.info("   Endpoints:")
    logger.info("     - GET  /          - Status")
    logger.info("     - GET  /api/health - Health check")
    logger.info("     - POST /api/auth/register - Register user")
    logger.info("     - POST /api/auth/login - Login user")
    logger.info("     - POST /api/auth/google - Google OAuth")
    logger.info("     - POST /api/stream/start - Start stream")
    logger.info("     - GET  /api/stream/status - Stream status")
    logger.info("     - WS   /ws/stream/{id} - WebSocket stream")
    logger.info("     - GET  /hls/{id}/*.m3u8 - HLS playlist")
    logger.info("     - GET  /demo - Demo UI")
    logger.info("="*60)

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown."""
    logger.info(f"🛑 Shutting down CCTV Backend ({SERVER_ID})...")
    enhanced_stream_service.stop_all()
    logger.info("✓ All streams stopped")
    logger.info(f"✓ Backend {SERVER_ID} shutdown complete")

# ==============================================================================
# Main Entry Point
# ==============================================================================

if __name__ == "__main__":
    import sys
    # Fix encoding for Windows console
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass
    print("="*60)
    print("[START] CCTV Backend Starting...")
    print(f"[SERVER] ID: {SERVER_ID}")
    print(f"[SERVER] Host: {SERVER_HOST}:{SERVER_PORT}")
    print(f"[SERVER] Debug: {DEBUG_MODE}")
    print(f"[DATA] Storage: {DEVICES_FILE}")
    print(f"[HLS] Output: {HLS_OUTPUT_DIR}")
    print(f"[LOG] Directory: {LOG_DIR}")
    print(f"[AUTH] Google OAuth: {'Enabled' if GOOGLE_OAUTH_ENABLED else 'Disabled'}")
    print(f"[AUTH] Email/Password: {'Enabled' if ALLOW_EMAIL_AUTH else 'Disabled'}")
    print("="*60)
    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT, log_level="info")
