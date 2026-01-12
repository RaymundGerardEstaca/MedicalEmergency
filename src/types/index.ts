export interface CameraConfig {
    name: string;
    localIP: string;
    rtspUsername: string;
    rtspPassword: string;
    cloudTunnelURL: string;
}

export interface ScannedDevice {
    ip: string;
    mac: string;
}

export interface StreamState {
    isLoading: boolean;
    isLive: boolean;
    hasError: boolean;
    errorMessage?: string;
}

export interface Device {
    id: string;
    name: string;
    ipAddress: string;
    isOnline: boolean;
    macAddress?: string;
}

export interface AlertSnapshot {
    id: string;
    imageUrl: string;
    timestamp: Date;
    detectedObject: string;
}
