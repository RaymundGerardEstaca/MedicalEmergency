// Type declarations for packages without @types
declare module 'react-native-ble-plx' {
    export class BleManager {
        startDeviceScan(
            serviceUUIDs: string[] | null,
            options: any | null,
            callback: (error: any, device: any) => void
        ): void;
        stopDeviceScan(): void;
        connectToDevice(deviceId: string): Promise<any>;
        destroy(): void;
    }

    export class Device {
        id: string;
        name: string;
        rssi: number;
        isConnectable: boolean;
        discoverAllServicesAndCharacteristics(): Promise<void>;
        writeCharacteristicWithResponseForService(
            serviceUUID: string,
            characteristicUUID: string,
            data: string
        ): Promise<void>;
        cancelConnection(): Promise<void>;
    }
}

declare module 'react-native-wifi-reborn' {
    interface WifiManager {
        getFrequency(): Promise<number | null>;
        getCurrentWifiSSID(): Promise<string | null>;
        getBSSID(): Promise<string | null>;
    }

    const WifiManager: WifiManager;
    export default WifiManager;
}

declare module 'buffer' {
    export const Buffer: {
        from(data: string, encoding?: string): {
            toString(encoding: string): string;
        };
    };
}

// Expo packages
declare module 'expo-av' {
    export interface AVPlaybackStatus {
        isLoaded: boolean;
        isPlaying: boolean;
        positionMillis: number;
        durationMillis: number;
        shouldPlay: boolean;
        isBuffering: boolean;
        rate: number;
        shouldCorrectPitch: boolean;
        volume: number;
        isMuted: boolean;
        isLooping: boolean;
        didJustFinish: boolean;
        error?: string;
    }

    export enum ResizeMode {
        CONTAIN = 'contain',
        COVER = 'cover',
        STRETCH = 'stretch'
    }

    export const Video: React.ComponentType<any>;

    export namespace Audio {
        class Sound {
            loadAsync(source: any): Promise<AVPlaybackStatus>;
            playAsync(): Promise<AVPlaybackStatus>;
            pauseAsync(): Promise<AVPlaybackStatus>;
            stopAsync(): Promise<AVPlaybackStatus>;
            unloadAsync(): Promise<void>;
        }
    }
}

declare module 'expo-status-bar' {
    export const StatusBar: any;
}

declare module 'expo-secure-store' {
    export function getItemAsync(key: string): Promise<string | null>;
    export function setItemAsync(key: string, value: string): Promise<void>;
    export function deleteItemAsync(key: string): Promise<void>;
}