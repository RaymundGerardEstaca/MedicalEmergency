"""
================================================================================
CCTV Backend Logger Service
================================================================================
Comprehensive logging with 60-70% coverage for debugging and monitoring.
Features:
- Multi-level logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Console and file output with rotation
- Sensitive data masking (passwords, IPs, tokens, credentials)
- Performance metrics and timing
- Structured log format with context
- Request/Response logging
- Stream lifecycle logging
================================================================================
"""

import logging
import logging.handlers
import os
import re
import sys
import time
import functools
import traceback
from datetime import datetime
from typing import Any, Callable, Dict, Optional, Union
from contextlib import contextmanager

# ==============================================================================
# Configuration Constants
# ==============================================================================

LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'backend.log')
ERROR_LOG_FILE = os.path.join(LOG_DIR, 'errors.log')
STREAM_LOG_FILE = os.path.join(LOG_DIR, 'streams.log')
ACCESS_LOG_FILE = os.path.join(LOG_DIR, 'access.log')

# Log rotation settings
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10 MB
BACKUP_COUNT = 5

# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# ==============================================================================
# Sensitive Data Patterns for Masking
# ==============================================================================

# Keys that should be FULLY masked (show nothing)
SENSITIVE_KEYS = frozenset({
    'password', 'passwd', 'pwd', 'secret', 'token', 'api_key', 'apikey',
    'access_token', 'refresh_token', 'auth_token', 'bearer', 'credentials',
    'private_key', 'privatekey', 'secret_key', 'secretkey', 'pin', 'cvv',
    'ssn', 'credit_card', 'card_number', 'wifi_password', 'wifipassword',
    'rtsp_password', 'camera_password', 'auth', 'authorization'
})

# Keys that should be PARTIALLY masked (show first/last few chars)
PARTIAL_MASK_KEYS = frozenset({
    'email', 'phone', 'ip', 'ip_address', 'ipaddress', 'mac', 'mac_address',
    'macaddress', 'device_id', 'deviceid', 'user_id', 'userid', 'session_id',
    'sessionid', 'uuid', 'ssid', 'bssid', 'rtsp_url', 'rtspurl', 'stream_url',
    'streamurl', 'url', 'host', 'hostname', 'ble_id', 'bleid'
})

# Regex patterns for sensitive data in log messages
SENSITIVE_PATTERNS = [
    # IPv4 addresses
    (re.compile(r'\b(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})\b'), r'\1.***.***.***'),
    # IPv6 addresses (simplified)
    (re.compile(r'\b([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b'), '[IPv6:****]'),
    # MAC addresses
    (re.compile(r'\b([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})\b'), r'\1**:**:**:**:**'),
    # Email addresses
    (re.compile(r'\b([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b'), r'\1[...]@***'),
    # Bearer tokens
    (re.compile(r'Bearer\s+[A-Za-z0-9\-_]+\.?[A-Za-z0-9\-_]*\.?[A-Za-z0-9\-_]*', re.I), 'Bearer [MASKED]'),
    # RTSP URLs with credentials: rtsp://user:pass@host
    (re.compile(r'rtsp://([^:]+):([^@]+)@([^/]+)'), r'rtsp://\1:****@\3'),
    # Generic password patterns in URLs
    (re.compile(r'(password|passwd|pwd|secret|token|key)=([^&\s]+)', re.I), r'\1=****'),
    # UUIDs (partial mask)
    (re.compile(r'\b([0-9a-fA-F]{8})-([0-9a-fA-F]{4})-([0-9a-fA-F]{4})-([0-9a-fA-F]{4})-([0-9a-fA-F]{12})\b'), r'\1-****-****-****-\5'),
    # Phone numbers (US format)
    (re.compile(r'\b(\d{3})[-.]?(\d{3})[-.]?(\d{4})\b'), r'\1-***-****'),
    # Credit card numbers (16 digits)
    (re.compile(r'\b(\d{4})[-\s]?(\d{4})[-\s]?(\d{4})[-\s]?(\d{4})\b'), r'\1-****-****-\4'),
    # Base64 encoded strings (long ones, likely tokens)
    (re.compile(r'[A-Za-z0-9+/]{40,}={0,2}'), '[BASE64_MASKED]'),
]

# ==============================================================================
# Custom Log Formatter with Masking
# ==============================================================================

class SensitiveDataFormatter(logging.Formatter):
    """
    Custom formatter that masks sensitive data in log messages.
    Provides 60-70% masking coverage for privacy and security.
    """
    
    def __init__(self, fmt: str = None, datefmt: str = None, style: str = '%'):
        super().__init__(fmt, datefmt, style)
    
    def format(self, record: logging.LogRecord) -> str:
        # First, format the record normally
        message = super().format(record)
        
        # Apply all sensitive data patterns
        for pattern, replacement in SENSITIVE_PATTERNS:
            message = pattern.sub(replacement, message)
        
        return message

    @staticmethod
    def mask_dict(data: Dict[str, Any], depth: int = 0) -> Dict[str, Any]:
        """
        Recursively mask sensitive keys in a dictionary.
        Returns a new dict with masked values.
        """
        if depth > 10:  # Prevent infinite recursion
            return {'[DEPTH_LIMIT]': '...'}
        
        masked = {}
        for key, value in data.items():
            key_lower = key.lower().replace('-', '_').replace(' ', '_')
            
            if key_lower in SENSITIVE_KEYS:
                masked[key] = '****MASKED****'
            elif key_lower in PARTIAL_MASK_KEYS:
                masked[key] = SensitiveDataFormatter._partial_mask(value)
            elif isinstance(value, dict):
                masked[key] = SensitiveDataFormatter.mask_dict(value, depth + 1)
            elif isinstance(value, list):
                masked[key] = [
                    SensitiveDataFormatter.mask_dict(v, depth + 1) if isinstance(v, dict) else v
                    for v in value
                ]
            else:
                masked[key] = value
        
        return masked
    
    @staticmethod
    def _partial_mask(value: Any) -> str:
        """Partially mask a value, showing first 3 and last 2 chars."""
        if value is None:
            return None
        
        s = str(value)
        if len(s) <= 5:
            return '***'
        
        return f"{s[:3]}***{s[-2:]}"

# ==============================================================================
# Logger Setup
# ==============================================================================

def setup_logger(
    name: str,
    level: int = logging.DEBUG,
    log_to_console: bool = True,
    log_to_file: bool = True
) -> logging.Logger:
    """
    Create and configure a logger with console and file handlers.
    
    Args:
        name: Logger name (usually module name)
        level: Minimum log level
        log_to_console: Whether to output to console
        log_to_file: Whether to output to file
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = SensitiveDataFormatter(
            fmt='%(asctime)s │ %(levelname)-8s │ %(name)-20s │ %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)
    
    # Main log file handler (rotating)
    if log_to_file:
        file_handler = logging.handlers.RotatingFileHandler(
            LOG_FILE,
            maxBytes=MAX_LOG_SIZE,
            backupCount=BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_format = SensitiveDataFormatter(
            fmt='%(asctime)s │ %(levelname)-8s │ %(name)-25s │ %(funcName)-20s │ %(lineno)4d │ %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
        
        # Error-only log file
        error_handler = logging.handlers.RotatingFileHandler(
            ERROR_LOG_FILE,
            maxBytes=MAX_LOG_SIZE,
            backupCount=BACKUP_COUNT,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_format)
        logger.addHandler(error_handler)
    
    return logger

def get_stream_logger() -> logging.Logger:
    """Get a dedicated logger for stream operations."""
    logger = logging.getLogger('StreamService')
    
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        
        # Stream-specific log file
        stream_handler = logging.handlers.RotatingFileHandler(
            STREAM_LOG_FILE,
            maxBytes=MAX_LOG_SIZE,
            backupCount=BACKUP_COUNT,
            encoding='utf-8'
        )
        stream_handler.setLevel(logging.DEBUG)
        stream_format = SensitiveDataFormatter(
            fmt='%(asctime)s │ %(levelname)-8s │ STREAM │ %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S.%f'
        )
        stream_handler.setFormatter(stream_format)
        logger.addHandler(stream_handler)
        
        # Also log to console
        console = logging.StreamHandler(sys.stdout)
        console.setLevel(logging.INFO)
        console.setFormatter(SensitiveDataFormatter(
            fmt='%(asctime)s │ %(levelname)-8s │ 🎥 STREAM │ %(message)s',
            datefmt='%H:%M:%S'
        ))
        logger.addHandler(console)
    
    return logger

def get_access_logger() -> logging.Logger:
    """Get a dedicated logger for API access logging."""
    logger = logging.getLogger('AccessLog')
    
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        access_handler = logging.handlers.RotatingFileHandler(
            ACCESS_LOG_FILE,
            maxBytes=MAX_LOG_SIZE,
            backupCount=BACKUP_COUNT,
            encoding='utf-8'
        )
        access_handler.setLevel(logging.INFO)
        access_format = SensitiveDataFormatter(
            fmt='%(asctime)s │ %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        access_handler.setFormatter(access_format)
        logger.addHandler(access_handler)
    
    return logger

# ==============================================================================
# Logging Decorators
# ==============================================================================

def log_function_call(logger: logging.Logger = None):
    """
    Decorator to log function entry, exit, and execution time.
    
    Usage:
        @log_function_call()
        def my_function(arg1, arg2):
            ...
    """
    def decorator(func: Callable) -> Callable:
        nonlocal logger
        if logger is None:
            logger = logging.getLogger(func.__module__)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            
            # Log entry with masked arguments
            masked_kwargs = SensitiveDataFormatter.mask_dict(kwargs) if kwargs else {}
            logger.debug(f"→ ENTER {func_name}() args_count={len(args)} kwargs={masked_kwargs}")
            
            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                logger.debug(f"← EXIT {func_name}() duration={elapsed_ms:.2f}ms success=True")
                return result
            except Exception as e:
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                logger.error(f"✖ FAIL {func_name}() duration={elapsed_ms:.2f}ms error={type(e).__name__}: {e}")
                raise
        
        return wrapper
    return decorator

def log_async_function_call(logger: logging.Logger = None):
    """
    Decorator to log async function entry, exit, and execution time.
    """
    def decorator(func: Callable) -> Callable:
        nonlocal logger
        if logger is None:
            logger = logging.getLogger(func.__module__)
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            func_name = func.__name__
            
            masked_kwargs = SensitiveDataFormatter.mask_dict(kwargs) if kwargs else {}
            logger.debug(f"→ ASYNC ENTER {func_name}() kwargs={masked_kwargs}")
            
            start_time = time.perf_counter()
            try:
                result = await func(*args, **kwargs)
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                logger.debug(f"← ASYNC EXIT {func_name}() duration={elapsed_ms:.2f}ms")
                return result
            except Exception as e:
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                logger.error(f"✖ ASYNC FAIL {func_name}() duration={elapsed_ms:.2f}ms error={type(e).__name__}: {e}")
                raise
        
        return wrapper
    return decorator

# ==============================================================================
# Context Managers for Logging
# ==============================================================================

@contextmanager
def log_operation(logger: logging.Logger, operation_name: str, **context):
    """
    Context manager for logging operations with timing.
    
    Usage:
        with log_operation(logger, "process_frame", camera_id="cam1"):
            # do work
    """
    masked_context = SensitiveDataFormatter.mask_dict(context) if context else {}
    logger.info(f"▶ START {operation_name} context={masked_context}")
    start_time = time.perf_counter()
    
    try:
        yield
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        logger.info(f"✓ COMPLETE {operation_name} duration={elapsed_ms:.2f}ms")
    except Exception as e:
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        logger.error(f"✖ FAILED {operation_name} duration={elapsed_ms:.2f}ms error={type(e).__name__}: {e}")
        logger.debug(f"Stack trace:\n{traceback.format_exc()}")
        raise

# ==============================================================================
# Specialized Logging Functions
# ==============================================================================

class StreamLogger:
    """
    Specialized logger for RTSP/HLS streaming operations.
    Provides structured logging for stream lifecycle events.
    """
    
    def __init__(self):
        self.logger = get_stream_logger()
        self._stream_stats: Dict[str, Dict] = {}
    
    def log_stream_start(self, stream_id: str, rtsp_url: str, output_format: str = 'hls'):
        """Log stream initialization."""
        # Mask the RTSP URL for security
        masked_url = re.sub(r'rtsp://([^:]+):([^@]+)@', r'rtsp://\1:****@', rtsp_url)
        
        self._stream_stats[stream_id] = {
            'started_at': datetime.now(),
            'frames_processed': 0,
            'errors': 0,
            'reconnects': 0
        }
        
        self.logger.info(f"🎬 STREAM_START stream_id={stream_id} url={masked_url} format={output_format}")
    
    def log_stream_stop(self, stream_id: str, reason: str = 'user_request'):
        """Log stream termination."""
        stats = self._stream_stats.pop(stream_id, {})
        duration = (datetime.now() - stats.get('started_at', datetime.now())).total_seconds() if stats else 0
        
        self.logger.info(
            f"🛑 STREAM_STOP stream_id={stream_id} reason={reason} "
            f"duration={duration:.1f}s frames={stats.get('frames_processed', 0)} "
            f"errors={stats.get('errors', 0)} reconnects={stats.get('reconnects', 0)}"
        )
    
    def log_frame_processed(self, stream_id: str, frame_size: int = 0, fps: float = 0.0):
        """Log frame processing (sampled - not every frame)."""
        if stream_id in self._stream_stats:
            self._stream_stats[stream_id]['frames_processed'] += 1
            count = self._stream_stats[stream_id]['frames_processed']
            
            # Log every 100th frame to avoid log spam
            if count % 100 == 0:
                self.logger.debug(
                    f"📹 FRAME stream_id={stream_id} count={count} size={frame_size}B fps={fps:.1f}"
                )
    
    def log_connection_error(self, stream_id: str, error: str, will_retry: bool = True):
        """Log connection errors with retry info."""
        if stream_id in self._stream_stats:
            self._stream_stats[stream_id]['errors'] += 1
        
        self.logger.warning(
            f"⚠️ STREAM_ERROR stream_id={stream_id} error={error} will_retry={will_retry}"
        )
    
    def log_reconnect(self, stream_id: str, attempt: int, max_attempts: int):
        """Log reconnection attempts."""
        if stream_id in self._stream_stats:
            self._stream_stats[stream_id]['reconnects'] += 1
        
        self.logger.info(
            f"🔄 RECONNECT stream_id={stream_id} attempt={attempt}/{max_attempts}"
        )
    
    def log_ffmpeg_output(self, stream_id: str, line: str, level: str = 'debug'):
        """Log FFmpeg subprocess output."""
        # Filter out noisy FFmpeg lines
        if any(skip in line.lower() for skip in ['frame=', 'size=', 'time=', 'bitrate=']):
            # Only log these at trace level (every 10th)
            if hasattr(self, '_ffmpeg_line_count'):
                self._ffmpeg_line_count += 1
            else:
                self._ffmpeg_line_count = 1
            
            if self._ffmpeg_line_count % 10 == 0:
                self.logger.debug(f"🎞️ FFMPEG [{stream_id}] {line.strip()}")
        else:
            # Log other lines at specified level
            log_method = getattr(self.logger, level, self.logger.debug)
            log_method(f"🎞️ FFMPEG [{stream_id}] {line.strip()}")
    
    def log_hls_segment(self, stream_id: str, segment_name: str, segment_duration: float):
        """Log HLS segment creation."""
        self.logger.debug(
            f"📦 HLS_SEGMENT stream_id={stream_id} segment={segment_name} duration={segment_duration:.2f}s"
        )

# ==============================================================================
# API Request/Response Logger
# ==============================================================================

class APILogger:
    """
    Logger for API requests and responses.
    Provides structured access logging with timing.
    """
    
    def __init__(self):
        self.logger = get_access_logger()
        self.main_logger = setup_logger('API')
    
    def log_request(
        self,
        method: str,
        path: str,
        client_ip: str = 'unknown',
        user_id: str = None,
        request_id: str = None
    ):
        """Log incoming API request."""
        # Mask client IP
        masked_ip = re.sub(r'(\d+)\.(\d+)\.(\d+)\.(\d+)', r'\1.***.***.***', client_ip)
        
        self.logger.info(
            f"→ {method} {path} client={masked_ip} user={user_id or 'anonymous'} req_id={request_id or '-'}"
        )
    
    def log_response(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        request_id: str = None
    ):
        """Log API response."""
        status_emoji = '✓' if 200 <= status_code < 400 else '✖'
        
        self.logger.info(
            f"← {status_emoji} {method} {path} status={status_code} duration={duration_ms:.2f}ms req_id={request_id or '-'}"
        )
        
        # Also log slow requests to main logger
        if duration_ms > 1000:
            self.main_logger.warning(
                f"SLOW_REQUEST {method} {path} took {duration_ms:.2f}ms"
            )
    
    def log_auth_event(self, event: str, user_email: str = None, success: bool = True):
        """Log authentication events."""
        masked_email = SensitiveDataFormatter._partial_mask(user_email) if user_email else 'unknown'
        
        if success:
            self.main_logger.info(f"🔐 AUTH {event} user={masked_email} success=True")
        else:
            self.main_logger.warning(f"🔐 AUTH {event} user={masked_email} success=False")

# ==============================================================================
# Performance Metrics Logger
# ==============================================================================

class MetricsLogger:
    """
    Logger for performance metrics and statistics.
    """
    
    def __init__(self):
        self.logger = setup_logger('Metrics')
        self._metrics: Dict[str, list] = {}
    
    def record_metric(self, name: str, value: float, unit: str = ''):
        """Record a metric value."""
        if name not in self._metrics:
            self._metrics[name] = []
        
        self._metrics[name].append(value)
        
        # Keep only last 100 values
        if len(self._metrics[name]) > 100:
            self._metrics[name] = self._metrics[name][-100:]
    
    def log_summary(self, name: str):
        """Log summary statistics for a metric."""
        if name not in self._metrics or not self._metrics[name]:
            return
        
        values = self._metrics[name]
        avg = sum(values) / len(values)
        min_val = min(values)
        max_val = max(values)
        
        self.logger.info(
            f"📊 METRIC {name}: avg={avg:.2f} min={min_val:.2f} max={max_val:.2f} samples={len(values)}"
        )
    
    def log_system_stats(self, cpu_percent: float, memory_mb: float, active_streams: int):
        """Log system resource usage."""
        self.logger.info(
            f"💻 SYSTEM cpu={cpu_percent:.1f}% memory={memory_mb:.0f}MB streams={active_streams}"
        )

# ==============================================================================
# Global Logger Instances
# ==============================================================================

# Main application logger
app_logger = setup_logger('Backend')

# Specialized loggers
stream_logger = StreamLogger()
api_logger = APILogger()
metrics_logger = MetricsLogger()

# ==============================================================================
# Convenience Functions
# ==============================================================================

def log_info(message: str, **kwargs):
    """Quick info log with optional context."""
    if kwargs:
        masked = SensitiveDataFormatter.mask_dict(kwargs)
        app_logger.info(f"{message} | {masked}")
    else:
        app_logger.info(message)

def log_error(message: str, exc: Exception = None, **kwargs):
    """Quick error log with optional exception."""
    if exc:
        app_logger.error(f"{message} | error={type(exc).__name__}: {exc}")
        app_logger.debug(traceback.format_exc())
    else:
        app_logger.error(message)

def log_debug(message: str, **kwargs):
    """Quick debug log."""
    if kwargs:
        masked = SensitiveDataFormatter.mask_dict(kwargs)
        app_logger.debug(f"{message} | {masked}")
    else:
        app_logger.debug(message)

def log_warning(message: str, **kwargs):
    """Quick warning log."""
    app_logger.warning(message)

# ==============================================================================
# Module Initialization Log
# ==============================================================================

app_logger.info("="*60)
app_logger.info("🚀 CCTV Backend Logger Service Initialized")
app_logger.info(f"   Log directory: {LOG_DIR}")
app_logger.info(f"   Main log file: {LOG_FILE}")
app_logger.info(f"   Error log file: {ERROR_LOG_FILE}")
app_logger.info(f"   Stream log file: {STREAM_LOG_FILE}")
app_logger.info(f"   Access log file: {ACCESS_LOG_FILE}")
app_logger.info(f"   Max log size: {MAX_LOG_SIZE // (1024*1024)} MB")
app_logger.info(f"   Backup count: {BACKUP_COUNT}")
app_logger.info("="*60)
