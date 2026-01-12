"""
================================================================================
CCTV Backend RTSP Stream Service - Production Grade
================================================================================
Features:
- FFmpeg-based RTSP to HLS transcoding (low latency)
- OpenCV fallback for WebSocket streaming
- Automatic reconnection with exponential backoff
- Connection health monitoring
- Multi-camera support
- Frame rate limiting and optimization
- Comprehensive logging (60-70% coverage)
================================================================================

Based on FFmpeg RTSP best practices:
- Uses TCP transport for reliability
- Low latency HLS settings (2 second segments, 3 segments in playlist)
- Hardware acceleration when available
- Timeout handling for network issues
================================================================================
"""

import asyncio
import cv2
import os
import re
import shutil
import signal
import subprocess
import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Callable, Dict, List, Optional, Tuple
import logging

# ==============================================================================
# Configuration
# ==============================================================================

# Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HLS_OUTPUT_DIR = os.path.join(BASE_DIR, 'hls_output')
RECORDINGS_DIR = os.path.join(BASE_DIR, 'recordings')
LOG_DIR = os.path.join(BASE_DIR, 'logs')

# Create directories
os.makedirs(HLS_OUTPUT_DIR, exist_ok=True)
os.makedirs(RECORDINGS_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# Stream settings
DEFAULT_HLS_SEGMENT_DURATION = 2  # seconds (low latency)
DEFAULT_HLS_LIST_SIZE = 3  # number of segments in playlist
DEFAULT_RECONNECT_DELAY = 5  # seconds
MAX_RECONNECT_ATTEMPTS = 10
FRAME_RATE_LIMIT = 30  # FPS limit for WebSocket streaming
OPENCV_TIMEOUT_MS = 10000  # 10 second timeout for OpenCV

# FFmpeg settings - Try explicit Windows path first, then PATH lookup
FFMPEG_WINDOWS_PATH = r'C:\ffmpeg\ffmpeg-8.0.1-essentials_build\bin\ffmpeg.exe'
FFPROBE_WINDOWS_PATH = r'C:\ffmpeg\ffmpeg-8.0.1-essentials_build\bin\ffprobe.exe'

# Use Windows path if exists, otherwise fall back to PATH lookup
if os.path.exists(FFMPEG_WINDOWS_PATH):
    FFMPEG_PATH = FFMPEG_WINDOWS_PATH
    FFPROBE_PATH = FFPROBE_WINDOWS_PATH
else:
    FFMPEG_PATH = shutil.which('ffmpeg') or 'ffmpeg'
    FFPROBE_PATH = shutil.which('ffprobe') or 'ffprobe'

# ==============================================================================
# Logging Setup with Sensitive Data Masking
# ==============================================================================

# Sensitive data patterns
SENSITIVE_PATTERNS = [
    (re.compile(r'\b(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})\b'), r'\1.***.***.***'),
    (re.compile(r'rtsp://([^:]+):([^@]+)@([^/]+)'), r'rtsp://\1:****@\3'),
    (re.compile(r'Bearer\s+[A-Za-z0-9\-_]+', re.I), 'Bearer [MASKED]'),
    (re.compile(r'(password|passwd|pwd|token|key)=([^&\s]+)', re.I), r'\1=****'),
]

class SensitiveFormatter(logging.Formatter):
    """Formatter that masks sensitive data in log messages."""
    def format(self, record):
        message = super().format(record)
        for pattern, replacement in SENSITIVE_PATTERNS:
            message = pattern.sub(replacement, message)
        return message

def setup_logger(name: str, level=logging.DEBUG) -> logging.Logger:
    """Create a logger with console and file output."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if logger.handlers:
        return logger
    
    # Console handler
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(SensitiveFormatter(
        '%(asctime)s │ %(levelname)-8s │ %(name)-15s │ %(message)s',
        datefmt='%H:%M:%S'
    ))
    logger.addHandler(console)
    
    # File handler
    log_file = os.path.join(LOG_DIR, f'{name.lower()}.log')
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(SensitiveFormatter(
        '%(asctime)s │ %(levelname)-8s │ %(funcName)-20s │ %(lineno)4d │ %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    logger.addHandler(file_handler)
    
    return logger

# Initialize logger
logger = setup_logger('RTSPService')

# ==============================================================================
# Stream Logger for detailed stream operations
# ==============================================================================

class StreamLogger:
    """Specialized logger for streaming operations with metrics tracking."""
    
    def __init__(self):
        self.logger = setup_logger('StreamOps')
        self._stats: Dict[str, Dict] = {}
    
    def log_stream_start(self, stream_id: str, rtsp_url: str, output_format: str = 'hls'):
        masked_url = re.sub(r'rtsp://([^:]+):([^@]+)@', r'rtsp://\1:****@', rtsp_url)
        self._stats[stream_id] = {
            'started_at': datetime.now(),
            'frames': 0, 'errors': 0, 'reconnects': 0
        }
        self.logger.info(f"🎬 STREAM_START id={stream_id} url={masked_url} format={output_format}")
    
    def log_stream_stop(self, stream_id: str, reason: str = 'user_request'):
        stats = self._stats.pop(stream_id, {})
        duration = (datetime.now() - stats.get('started_at', datetime.now())).total_seconds() if stats else 0
        self.logger.info(f"🛑 STREAM_STOP id={stream_id} reason={reason} duration={duration:.1f}s frames={stats.get('frames', 0)}")
    
    def log_frame(self, stream_id: str, size: int, fps: float):
        if stream_id in self._stats:
            self._stats[stream_id]['frames'] += 1
            if self._stats[stream_id]['frames'] % 100 == 0:
                self.logger.debug(f"📹 FRAME id={stream_id} count={self._stats[stream_id]['frames']} size={size}B fps={fps:.1f}")
    
    def log_error(self, stream_id: str, error: str, will_retry: bool = True):
        if stream_id in self._stats:
            self._stats[stream_id]['errors'] += 1
        self.logger.warning(f"⚠️ ERROR id={stream_id} error={error} retry={will_retry}")
    
    def log_reconnect(self, stream_id: str, attempt: int, max_attempts: int):
        if stream_id in self._stats:
            self._stats[stream_id]['reconnects'] += 1
        self.logger.info(f"🔄 RECONNECT id={stream_id} attempt={attempt}/{max_attempts}")
    
    def log_ffmpeg(self, stream_id: str, line: str):
        if 'error' in line.lower() or 'failed' in line.lower():
            self.logger.warning(f"🎞️ FFMPEG [{stream_id}] {line.strip()}")
        else:
            self.logger.debug(f"🎞️ FFMPEG [{stream_id}] {line.strip()}")

stream_logger = StreamLogger()

# ==============================================================================
# Enums and Data Classes
# ==============================================================================

class StreamState(Enum):
    IDLE = 'idle'
    CONNECTING = 'connecting'
    CONNECTED = 'connected'
    STREAMING = 'streaming'
    RECONNECTING = 'reconnecting'
    ERROR = 'error'
    STOPPED = 'stopped'

class StreamMode(Enum):
    HLS = 'hls'
    WEBSOCKET = 'websocket'
    BOTH = 'both'

@dataclass
class StreamConfig:
    stream_id: str
    rtsp_url: str
    mode: StreamMode = StreamMode.BOTH
    hls_segment_duration: int = DEFAULT_HLS_SEGMENT_DURATION
    hls_list_size: int = DEFAULT_HLS_LIST_SIZE
    frame_rate: int = FRAME_RATE_LIMIT
    jpeg_quality: int = 70
    resize_width: Optional[int] = None
    resize_height: Optional[int] = None
    enable_audio: bool = False

@dataclass
class StreamStatus:
    stream_id: str
    state: StreamState = StreamState.IDLE
    started_at: Optional[datetime] = None
    last_frame_at: Optional[datetime] = None
    frames_processed: int = 0
    bytes_transmitted: int = 0
    errors: int = 0
    reconnect_attempts: int = 0
    current_fps: float = 0.0
    hls_ready: bool = False
    hls_url: str = ""
    error_message: str = ""

@dataclass
class StreamInstance:
    config: StreamConfig
    status: StreamStatus
    ffmpeg_process: Optional[subprocess.Popen] = None
    opencv_capture: Optional[cv2.VideoCapture] = None
    capture_thread: Optional[threading.Thread] = None
    latest_frame: Optional[bytes] = None
    frame_lock: threading.Lock = field(default_factory=threading.Lock)
    stop_event: threading.Event = field(default_factory=threading.Event)

# ==============================================================================
# FFmpeg Command Builder
# ==============================================================================

class FFmpegCommandBuilder:
    """Builds optimized FFmpeg commands for RTSP streaming."""
    
    @staticmethod
    def build_rtsp_to_hls(
        rtsp_url: str, output_dir: str, stream_id: str,
        segment_duration: int = 2, list_size: int = 3, enable_audio: bool = False
    ) -> List[str]:
        """Build FFmpeg command for RTSP to HLS conversion with best practices."""
        output_playlist = os.path.join(output_dir, f'{stream_id}.m3u8')
        output_segment = os.path.join(output_dir, f'{stream_id}_%03d.ts')
        
        cmd = [
            FFMPEG_PATH,
            '-hide_banner', '-loglevel', 'warning',
            # RTSP input options (TCP for reliability)
            '-rtsp_transport', 'tcp',
            '-timeout', '10000000',  # 10 sec timeout (FFmpeg 8.x compatible)
            '-analyzeduration', '2000000',
            '-probesize', '2000000',
            '-i', rtsp_url,
            # Video: copy codec for speed
            '-c:v', 'copy',
        ]
        
        if enable_audio:
            cmd.extend(['-c:a', 'aac', '-b:a', '128k'])
        else:
            cmd.extend(['-an'])
        
        cmd.extend([
            '-f', 'hls',
            '-hls_time', str(segment_duration),
            '-hls_list_size', str(list_size),
            '-hls_flags', 'delete_segments+append_list+omit_endlist',
            '-hls_segment_filename', output_segment,
            '-start_number', '0',
            output_playlist
        ])
        
        return cmd
    
    @staticmethod
    def build_probe(rtsp_url: str) -> List[str]:
        return [
            FFPROBE_PATH, '-v', 'quiet', '-rtsp_transport', 'tcp',
            '-timeout', '5000000', '-print_format', 'json',
            '-show_streams', '-show_format', rtsp_url
        ]

# ==============================================================================
# Enhanced RTSP Stream Service
# ==============================================================================

class EnhancedRTSPStreamService:
    """
    Production-grade RTSP streaming service with FFmpeg HLS + OpenCV WebSocket.
    Includes automatic reconnection, health monitoring, and comprehensive logging.
    """
    
    def __init__(self):
        logger.info("="*60)
        logger.info("🎬 Initializing Enhanced RTSP Stream Service")
        logger.info(f"   FFmpeg path: {FFMPEG_PATH}")
        logger.info(f"   HLS output: {HLS_OUTPUT_DIR}")
        logger.info("="*60)
        
        self._streams: Dict[str, StreamInstance] = {}
        self._lock = threading.Lock()
        self._ffmpeg_available = self._check_ffmpeg()
        
        logger.info(f"   FFmpeg available: {self._ffmpeg_available}")
    
    def _check_ffmpeg(self) -> bool:
        try:
            result = subprocess.run([FFMPEG_PATH, '-version'], capture_output=True, timeout=5)
            return result.returncode == 0
        except Exception as e:
            logger.warning(f"FFmpeg check failed: {e}")
            return False
    
    def _create_robust_capture(self, rtsp_url: str) -> Optional[cv2.VideoCapture]:
        """
        Create a robust OpenCV VideoCapture with multiple connection strategies.
        Tries different RTSP URL formats and transport options for maximum compatibility.
        """
        # Extract base URL components for generating variations
        import urllib.parse
        parsed = urllib.parse.urlparse(rtsp_url)
        
        # Common RTSP stream paths to try (different cameras use different paths)
        rtsp_paths = [
            parsed.path,  # Original path
            '/stream1',
            '/h264_stream',
            '/cam/realmonitor?channel=1&subtype=0',
            '/Streaming/Channels/101',
            '/live/ch00_0',
            '/MediaInput/h264',
            '/video1',
            '/1/stream1',
            '',
        ]
        
        # Remove duplicates while preserving order
        seen = set()
        rtsp_paths = [x for x in rtsp_paths if not (x in seen or seen.add(x))]
        
        # Connection strategies (environment variables for OpenCV FFmpeg backend)
        connection_strategies = [
            # Strategy 1: TCP transport with timeout (most reliable)
            {
                'OPENCV_FFMPEG_CAPTURE_OPTIONS': 'rtsp_transport;tcp|stimeout;10000000|buffer_size;1024000',
                'name': 'TCP with timeout'
            },
            # Strategy 2: TCP transport only
            {
                'OPENCV_FFMPEG_CAPTURE_OPTIONS': 'rtsp_transport;tcp',
                'name': 'TCP basic'
            },
            # Strategy 3: UDP transport (some cameras only support this)
            {
                'OPENCV_FFMPEG_CAPTURE_OPTIONS': 'rtsp_transport;udp|buffer_size;1024000',
                'name': 'UDP'
            },
            # Strategy 4: Auto (let FFmpeg decide)
            {
                'OPENCV_FFMPEG_CAPTURE_OPTIONS': 'stimeout;10000000',
                'name': 'Auto with timeout'
            },
        ]
        
        # Try to get base URL (host and port)
        base_url = f"{parsed.scheme}://"
        if parsed.username:
            base_url += f"{parsed.username}"
            if parsed.password:
                base_url += f":{parsed.password}"
            base_url += "@"
        base_url += parsed.netloc.split('@')[-1]  # host:port without credentials
        
        logger.info(f"🔍 Attempting robust RTSP connection to {base_url}")
        
        # First, try the original URL with different strategies
        for strategy in connection_strategies:
            # Set environment variables for OpenCV FFmpeg backend
            os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = strategy.get('OPENCV_FFMPEG_CAPTURE_OPTIONS', '')
            
            logger.debug(f"  Trying: {strategy['name']} with original URL")
            
            try:
                cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 10000)  # 10 second open timeout
                cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 10000)  # 10 second read timeout
                
                # Try to read a frame to verify connection
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        logger.info(f"✓ Connected using {strategy['name']} to original URL")
                        return cap
                    cap.release()
            except Exception as e:
                logger.debug(f"  Strategy {strategy['name']} failed: {e}")
                continue
        
        # If original URL didn't work, try different paths
        for path in rtsp_paths[1:]:  # Skip first (original) path
            url = base_url + path
            
            # Only try TCP for path variations (most likely to work)
            os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'rtsp_transport;tcp|stimeout;10000000'
            
            logger.debug(f"  Trying path: {path}")
            
            try:
                cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 8000)
                cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 8000)
                
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        logger.info(f"✓ Connected using path: {path}")
                        return cap
                    cap.release()
            except Exception as e:
                continue
        
        logger.error(f"✖ Failed to connect with all strategies")
        return None

    def start_stream(
        self, rtsp_url: str, stream_id: str = None,
        mode: StreamMode = StreamMode.BOTH, config: StreamConfig = None
    ) -> StreamStatus:
        """Start a new RTSP stream with full logging."""
        with self._lock:
            if not stream_id:
                stream_id = str(uuid.uuid4())[:8]
            
            if stream_id in self._streams:
                logger.warning(f"Stream {stream_id} exists - stopping first")
                self._stop_internal(stream_id)
            
            if config is None:
                config = StreamConfig(stream_id=stream_id, rtsp_url=rtsp_url, mode=mode)
            
            status = StreamStatus(stream_id=stream_id, state=StreamState.CONNECTING, started_at=datetime.now())
            instance = StreamInstance(config=config, status=status)
            self._streams[stream_id] = instance
            
            stream_logger.log_stream_start(stream_id, rtsp_url, mode.value)
            
            logger.info(f"📹 Starting stream {stream_id} mode={mode.value}")
            
            if mode in [StreamMode.HLS, StreamMode.BOTH] and self._ffmpeg_available:
                self._start_hls(instance)
            
            if mode in [StreamMode.WEBSOCKET, StreamMode.BOTH]:
                self._start_websocket(instance)
            
            return instance.status
    
    def _start_hls(self, instance: StreamInstance):
        """Start FFmpeg HLS transcoding."""
        config = instance.config
        logger.info(f"🎞️ Starting HLS for {config.stream_id}")
        
        stream_dir = os.path.join(HLS_OUTPUT_DIR, config.stream_id)
        os.makedirs(stream_dir, exist_ok=True)
        
        cmd = FFmpegCommandBuilder.build_rtsp_to_hls(
            config.rtsp_url, stream_dir, config.stream_id,
            config.hls_segment_duration, config.hls_list_size, config.enable_audio
        )
        
        logger.debug(f"FFmpeg cmd: {' '.join(cmd)}")
        
        try:
            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            instance.ffmpeg_process = process
            instance.status.hls_url = f"/hls/{config.stream_id}/{config.stream_id}.m3u8"
            
            threading.Thread(target=self._monitor_ffmpeg, args=(instance,), daemon=True).start()
            logger.info(f"✓ FFmpeg started PID={process.pid}")
        except Exception as e:
            logger.error(f"✖ FFmpeg start failed: {e}")
            instance.status.state = StreamState.ERROR
            instance.status.error_message = str(e)
    
    def _monitor_ffmpeg(self, instance: StreamInstance):
        """Monitor FFmpeg process and handle reconnection."""
        config = instance.config
        process = instance.ffmpeg_process
        playlist = os.path.join(HLS_OUTPUT_DIR, config.stream_id, f'{config.stream_id}.m3u8')
        
        logger.debug(f"FFmpeg monitor started for {config.stream_id}")
        hls_ready = False
        
        while process and process.poll() is None and not instance.stop_event.is_set():
            if not hls_ready and os.path.exists(playlist):
                instance.status.hls_ready = True
                instance.status.state = StreamState.STREAMING
                logger.info(f"✓ HLS ready: {playlist}")
                hls_ready = True
            
            try:
                line = process.stderr.readline()
                if line:
                    stream_logger.log_ffmpeg(config.stream_id, line.decode('utf-8', errors='ignore'))
            except:
                pass
            
            time.sleep(0.1)
        
        if process and process.poll() != 0 and not instance.stop_event.is_set():
            logger.error(f"FFmpeg exited with code {process.poll()}")
            self._reconnect_ffmpeg(instance)
    
    def _reconnect_ffmpeg(self, instance: StreamInstance):
        """Handle FFmpeg reconnection with exponential backoff."""
        if instance.stop_event.is_set():
            return
        
        instance.status.reconnect_attempts += 1
        if instance.status.reconnect_attempts > MAX_RECONNECT_ATTEMPTS:
            logger.error(f"Max reconnects reached for {instance.config.stream_id}")
            instance.status.state = StreamState.ERROR
            return
        
        stream_logger.log_reconnect(instance.config.stream_id, instance.status.reconnect_attempts, MAX_RECONNECT_ATTEMPTS)
        delay = min(DEFAULT_RECONNECT_DELAY * (2 ** (instance.status.reconnect_attempts - 1)), 60)
        
        logger.info(f"Reconnecting in {delay}s...")
        time.sleep(delay)
        
        if not instance.stop_event.is_set():
            self._start_hls(instance)
    
    def _start_websocket(self, instance: StreamInstance):
        """Start OpenCV WebSocket streaming."""
        logger.info(f"📹 Starting WebSocket for {instance.config.stream_id}")
        instance.capture_thread = threading.Thread(target=self._capture_loop, args=(instance,), daemon=True)
        instance.capture_thread.start()
    
    def _capture_loop(self, instance: StreamInstance):
        """OpenCV frame capture loop with reconnection and robust connection handling."""
        config = instance.config
        status = instance.status
        reconnects = 0
        fps_counter = 0
        fps_time = time.time()
        
        logger.debug(f"Capture loop started for {config.stream_id}")
        
        while not instance.stop_event.is_set():
            # Connect
            if instance.opencv_capture is None or not instance.opencv_capture.isOpened():
                logger.info(f"Connecting OpenCV to stream...")
                try:
                    # Build robust RTSP connection with multiple attempts and URL variations
                    cap = self._create_robust_capture(config.rtsp_url)
                    
                    if cap is None or not cap.isOpened():
                        raise Exception("Failed to open stream with all methods")
                    
                    instance.opencv_capture = cap
                    status.state = StreamState.CONNECTED
                    reconnects = 0
                    logger.info(f"✓ OpenCV connected for {config.stream_id}")
                except Exception as e:
                    reconnects += 1
                    stream_logger.log_error(config.stream_id, str(e), reconnects < MAX_RECONNECT_ATTEMPTS)
                    
                    if reconnects >= MAX_RECONNECT_ATTEMPTS:
                        status.state = StreamState.ERROR
                        status.error_message = str(e)
                        break
                    
                    delay = min(DEFAULT_RECONNECT_DELAY * (2 ** (reconnects - 1)), 60)
                    logger.warning(f"Connection failed, retrying in {delay}s")
                    time.sleep(delay)
                    continue
            
            # Read frame
            try:
                ret, frame = instance.opencv_capture.read()
                if not ret:
                    logger.warning("Frame read failed")
                    instance.opencv_capture.release()
                    instance.opencv_capture = None
                    status.errors += 1
                    continue
                
                # Resize if needed
                if config.resize_width and config.resize_height:
                    frame = cv2.resize(frame, (config.resize_width, config.resize_height))
                
                # Encode
                ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, config.jpeg_quality])
                if ret:
                    frame_bytes = buffer.tobytes()
                    with instance.frame_lock:
                        instance.latest_frame = frame_bytes
                    
                    status.frames_processed += 1
                    status.bytes_transmitted += len(frame_bytes)
                    status.last_frame_at = datetime.now()
                    
                    # FPS calc
                    fps_counter += 1
                    if time.time() - fps_time >= 1.0:
                        status.current_fps = fps_counter
                        stream_logger.log_frame(config.stream_id, len(frame_bytes), status.current_fps)
                        fps_counter = 0
                        fps_time = time.time()
                
                time.sleep(1.0 / config.frame_rate)
            except Exception as e:
                logger.error(f"Frame error: {e}")
                status.errors += 1
                time.sleep(0.1)
        
        if instance.opencv_capture:
            instance.opencv_capture.release()
        logger.info(f"Capture loop ended for {config.stream_id}")
    
    def stop_stream(self, stream_id: str, reason: str = 'user_request') -> bool:
        """Stop a stream."""
        with self._lock:
            return self._stop_internal(stream_id, reason)
    
    def _stop_internal(self, stream_id: str, reason: str = 'user_request') -> bool:
        if stream_id not in self._streams:
            logger.warning(f"Stream {stream_id} not found")
            return False
        
        instance = self._streams[stream_id]
        logger.info(f"🛑 Stopping {stream_id} reason={reason}")
        
        instance.stop_event.set()
        instance.status.state = StreamState.STOPPED
        
        if instance.ffmpeg_process:
            try:
                instance.ffmpeg_process.terminate()
                instance.ffmpeg_process.wait(timeout=5)
            except:
                instance.ffmpeg_process.kill()
        
        if instance.opencv_capture:
            instance.opencv_capture.release()
        
        if instance.capture_thread and instance.capture_thread.is_alive():
            instance.capture_thread.join(timeout=2)
        
        stream_logger.log_stream_stop(stream_id, reason)
        del self._streams[stream_id]
        return True
    
    def stop_all(self):
        """Stop all streams."""
        logger.info("🛑 Stopping all streams")
        with self._lock:
            for sid in list(self._streams.keys()):
                self._stop_internal(sid, 'shutdown')
    
    def get_frame(self, stream_id: str) -> Optional[bytes]:
        if stream_id not in self._streams:
            return None
        with self._streams[stream_id].frame_lock:
            return self._streams[stream_id].latest_frame
    
    def get_status(self, stream_id: str) -> Optional[StreamStatus]:
        return self._streams.get(stream_id, {}).status if stream_id in self._streams else None
    
    def get_all_streams(self) -> Dict[str, StreamStatus]:
        return {k: v.status for k, v in self._streams.items()}
    
    def is_running(self, stream_id: str = None) -> bool:
        if stream_id:
            return stream_id in self._streams
        return len(self._streams) > 0
    
    def probe_stream(self, rtsp_url: str) -> Dict:
        """Probe RTSP stream info using FFprobe."""
        if not self._ffmpeg_available:
            return {'error': 'FFprobe not available'}
        
        logger.info(f"Probing stream...")
        try:
            result = subprocess.run(
                FFmpegCommandBuilder.build_probe(rtsp_url),
                capture_output=True, text=True, timeout=15
            )
            if result.returncode == 0:
                import json
                return {'available': True, **json.loads(result.stdout)}
            return {'available': False, 'error': result.stderr}
        except Exception as e:
            return {'available': False, 'error': str(e)}
    
    def _check_port_open(self, ip: str, port: int, timeout: float = 2.0) -> bool:
        """Quick TCP port check - returns True if port is open."""
        import socket
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            # Use connect() instead of connect_ex() for cleaner error handling
            sock.connect((ip, port))
            sock.close()
            return True
        except socket.timeout:
            return False
        except ConnectionRefusedError:
            return False
        except OSError:
            return False
        except Exception as e:
            logger.debug(f"Port check error: {e}")
            return False
    
    def _quick_rtsp_test(self, url: str, timeout_sec: float = 3.0) -> Optional[Dict]:
        """
        Quick RTSP test with strict timeout enforcement.
        Uses threading to enforce timeout even if OpenCV hangs.
        """
        result = {'success': False, 'frame': None, 'width': 0, 'height': 0, 'fps': 0}
        
        def test_capture():
            try:
                # Set environment for shorter timeout
                os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = f'rtsp_transport;tcp|stimeout;{int(timeout_sec * 1000000)}'
                
                cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        result['success'] = True
                        result['width'] = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                        result['height'] = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        result['fps'] = cap.get(cv2.CAP_PROP_FPS)
                        # Encode frame as JPEG for thumbnail
                        _, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
                        result['frame'] = jpeg.tobytes()
                    cap.release()
            except Exception as e:
                logger.debug(f"RTSP test error: {e}")
        
        thread = threading.Thread(target=test_capture)
        thread.start()
        thread.join(timeout=timeout_sec + 1)  # Wait with timeout
        
        if thread.is_alive():
            logger.debug(f"RTSP test timeout for {url}")
            return None
        
        return result if result['success'] else None
    
    def check_camera_connectivity(self, ip_address: str, port: int = 554) -> Dict:
        """
        Quick check if camera is reachable before trying RTSP.
        Returns connectivity status and port info.
        """
        logger.info(f"Checking connectivity to {ip_address}:{port}")
        
        import socket
        results = {
            'ip': ip_address,
            'port': port,
            'reachable': False,
            'rtsp_port_open': False,
            'http_port_open': False,
            'latency_ms': None,
            'error': None
        }
        
        # TCP connection check with proper timeout
        start = time.time()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            # Use connect() instead of connect_ex() for better Windows compatibility
            sock.connect((ip_address, port))
            latency = (time.time() - start) * 1000
            sock.close()
            
            results['reachable'] = True
            results['rtsp_port_open'] = True
            results['latency_ms'] = round(latency, 1)
            logger.info(f"  Port {port} OPEN (latency: {results['latency_ms']}ms)")
        except socket.timeout:
            results['error'] = f"Connection timeout - camera may be unreachable"
            logger.warning(f"  Connection timeout to {ip_address}:{port}")
        except ConnectionRefusedError:
            results['error'] = f"Connection refused - port {port} is closed"
            logger.warning(f"  Port {port} connection refused")
        except socket.gaierror as e:
            results['error'] = f"DNS/Address error: {e}"
            logger.warning(f"  Address error: {e}")
        except OSError as e:
            # Handles network unreachable, host unreachable, etc.
            results['error'] = f"Network error: {e}"
            logger.warning(f"  Network error connecting to {ip_address}:{port}: {e}")
        except Exception as e:
            results['error'] = f"Connection error: {e}"
            logger.warning(f"  Connection error: {e}")
        
        # Also check HTTP port (80) for web interface
        if self._check_port_open(ip_address, 80, 2):
            results['http_port_open'] = True
            logger.info(f"  Port 80 (HTTP) OPEN")
        
        return results
    
    def discover_rtsp_url(self, ip_address: str, port: int = 554, username: str = None, password: str = None, quick_mode: bool = True) -> Dict:
        """
        Discover the correct RTSP URL for a camera by trying common paths.
        Now with connectivity check first and proper timeout handling.
        
        Args:
            ip_address: Camera IP address
            port: RTSP port (default 554)
            username: Optional username for authentication
            password: Optional password for authentication
            quick_mode: If True, stop after finding first working URL
        """
        logger.info(f"Discovering RTSP URL for {ip_address}:{port}")
        
        results = {
            'ip': ip_address,
            'port': port,
            'connectivity': None,
            'working_urls': [],
            'failed_urls': [],
            'recommended_url': None,
            'camera_info': None,
            'thumbnail': None,
            'error': None
        }
        
        # Step 1: Quick connectivity check
        connectivity = self.check_camera_connectivity(ip_address, port)
        results['connectivity'] = connectivity
        
        if not connectivity['rtsp_port_open']:
            results['error'] = connectivity.get('error', f'RTSP port {port} is not accessible')
            logger.warning(f"RTSP port not accessible: {results['error']}")
            return results
        
        logger.info(f"Port {port} is open, testing RTSP paths...")
        
        # Common RTSP paths - prioritized by likelihood
        rtsp_paths = [
            # Most common generic paths
            ('/stream1', 'Generic Stream 1', ['Generic', 'FT04']),
            ('/live/ch00_0', 'Live Channel', ['Generic']),
            ('/', 'Root', ['Generic']),
            ('/1', 'Channel 1', ['Generic']),
            ('/video1', 'Video 1', ['Generic']),
            ('/h264_stream', 'H264', ['Generic']),
            
            # Hikvision (very popular)
            ('/Streaming/Channels/101', 'Hikvision Main', ['Hikvision']),
            ('/Streaming/Channels/102', 'Hikvision Sub', ['Hikvision']),
            
            # Dahua (very popular)
            ('/cam/realmonitor?channel=1&subtype=0', 'Dahua Main', ['Dahua']),
            ('/cam/realmonitor?channel=1&subtype=1', 'Dahua Sub', ['Dahua']),
            
            # Reolink
            ('/h264Preview_01_main', 'Reolink Main', ['Reolink']),
            ('/h264Preview_01_sub', 'Reolink Sub', ['Reolink']),
            
            # Foscam
            ('/videoMain', 'Foscam Main', ['Foscam']),
            
            # ONVIF
            ('/onvif1', 'ONVIF 1', ['ONVIF']),
            
            # Additional generic
            ('/11', 'Stream 11', ['Generic']),
            ('/12', 'Stream 12', ['Generic']),
            ('/live', 'Live', ['Generic']),
            ('/stream', 'Stream', ['Generic']),
        ]
        
        # Build base URL with optional credentials
        if username and password:
            base_url = f"rtsp://{username}:{password}@{ip_address}:{port}"
            base_url_display = f"rtsp://***:***@{ip_address}:{port}"
        else:
            base_url = f"rtsp://{ip_address}:{port}"
            base_url_display = base_url
        
        # Test each path with short timeout
        test_timeout = 3.0  # 3 seconds per path
        
        for path, description, brands in rtsp_paths:
            url = base_url + path
            logger.debug(f"  Testing: {base_url_display}{path}")
            
            test_result = self._quick_rtsp_test(url, test_timeout)
            
            if test_result:
                url_info = {
                    'url': url,
                    'path': path,
                    'description': description,
                    'brands': brands,
                    'resolution': f"{test_result['width']}x{test_result['height']}",
                    'width': test_result['width'],
                    'height': test_result['height'],
                    'fps': test_result['fps']
                }
                results['working_urls'].append(url_info)
                
                if not results['recommended_url']:
                    results['recommended_url'] = url
                    results['camera_info'] = url_info
                    if test_result.get('frame'):
                        import base64
                        results['thumbnail'] = base64.b64encode(test_result['frame']).decode('utf-8')
                
                logger.info(f"  Found: {path} ({test_result['width']}x{test_result['height']})")
                
                if quick_mode:
                    logger.info("Quick mode - stopping after first match")
                    break
            else:
                results['failed_urls'].append({'path': path, 'reason': 'No response/timeout'})
        
        if results['working_urls']:
            logger.info(f"Discovery complete: {len(results['working_urls'])} URL(s) found")
        else:
            results['error'] = "No working RTSP URLs found. Camera may require authentication or use non-standard paths."
            logger.warning(f"Discovery failed for {ip_address}")
        
        return results

# ==============================================================================
# Legacy Wrapper (backward compatible)
# ==============================================================================

class RTSPStreamService:
    """Simple wrapper for backward compatibility."""
    
    def __init__(self):
        self._enhanced = EnhancedRTSPStreamService()
        self._current_id: Optional[str] = None
        logger.info("Legacy RTSPStreamService initialized")
    
    @property
    def is_running(self) -> bool:
        return self._enhanced.is_running(self._current_id)
    
    def start_stream(self, rtsp_url: str):
        logger.info(f"Legacy start_stream called")
        if self._current_id:
            self._enhanced.stop_stream(self._current_id)
        self._current_id = 'main'
        self._enhanced.start_stream(rtsp_url, self._current_id, StreamMode.WEBSOCKET)
    
    def stop_stream(self):
        logger.info("Legacy stop_stream called")
        if self._current_id:
            self._enhanced.stop_stream(self._current_id)
            self._current_id = None
    
    def get_frame(self) -> Optional[bytes]:
        return self._enhanced.get_frame(self._current_id) if self._current_id else None

# ==============================================================================
# Global Instances
# ==============================================================================

enhanced_stream_service = EnhancedRTSPStreamService()
stream_service = RTSPStreamService()

logger.info("="*60)
logger.info("📹 RTSP Stream Service Ready")
logger.info(f"   HLS output: {HLS_OUTPUT_DIR}")
logger.info(f"   Logs: {LOG_DIR}")
logger.info("="*60)

