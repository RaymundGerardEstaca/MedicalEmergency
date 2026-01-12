// Jest setup file
import '@testing-library/jest-native/extend-expect';
import { Buffer } from 'buffer';

// Add Buffer to global scope for tests
global.Buffer = Buffer;

// Mock react-native-ble-plx
jest.mock('react-native-ble-plx', () => {
    // Create mock device with all required methods
    const createMockDevice = (overrides = {}) => ({
        id: 'test-device-id',
        name: 'Test Device',
        rssi: -50,
        serviceUUIDs: [],
        localName: null,
        discoverAllServicesAndCharacteristics: jest.fn().mockResolvedValue(undefined),
        writeCharacteristicWithResponseForService: jest.fn().mockResolvedValue({}),
        monitorCharacteristicForService: jest.fn(),
        ...overrides,
    });

    const defaultMockDevice = createMockDevice();

    return {
        BleManager: jest.fn().mockImplementation(() => ({
            startDeviceScan: jest.fn(),
            stopDeviceScan: jest.fn(),
            connectToDevice: jest.fn().mockResolvedValue(defaultMockDevice),
            isDeviceConnected: jest.fn(),
            discoverAllServicesAndCharacteristicsForDevice: jest.fn().mockResolvedValue(defaultMockDevice),
            writeCharacteristicWithResponseForDevice: jest.fn(),
            monitorCharacteristicForDevice: jest.fn(),
            cancelDeviceConnection: jest.fn().mockResolvedValue(defaultMockDevice),
            state: jest.fn().mockResolvedValue('PoweredOn'),
            destroy: jest.fn(),
        })),
        State: {
            PoweredOn: 'PoweredOn',
            PoweredOff: 'PoweredOff',
        },
    };
});

// Mock @react-native-community/netinfo
jest.mock('@react-native-community/netinfo', () => ({
    fetch: jest.fn(() => Promise.resolve({
        type: 'wifi',
        isConnected: true,
        isInternetReachable: true,
        details: {
            ipAddress: '192.168.1.100',
        },
    })),
    addEventListener: jest.fn(),
}));

// Mock react-native-wifi-reborn
jest.mock('react-native-wifi-reborn', () => ({
    default: {
        getCurrentWifiSSID: jest.fn().mockResolvedValue('TestNetwork'),
        getFrequency: jest.fn().mockResolvedValue(2450), // 2.4 GHz
        reScanAndLoadWifiList: jest.fn().mockResolvedValue([]),
        getIP: jest.fn().mockResolvedValue('192.168.1.100'),
    },
    getCurrentWifiSSID: jest.fn().mockResolvedValue('TestNetwork'),
    getFrequency: jest.fn().mockResolvedValue(2450),
    reScanAndLoadWifiList: jest.fn().mockResolvedValue([]),
    getIP: jest.fn().mockResolvedValue('192.168.1.100'),
}));

// Mock react-native-permissions
jest.mock('react-native-permissions', () => ({
    request: jest.fn(),
    check: jest.fn(),
    PERMISSIONS: {
        ANDROID: {
            BLUETOOTH_SCAN: 'android.permission.BLUETOOTH_SCAN',
            BLUETOOTH_CONNECT: 'android.permission.BLUETOOTH_CONNECT',
            ACCESS_FINE_LOCATION: 'android.permission.ACCESS_FINE_LOCATION',
        },
    },
    RESULTS: {
        GRANTED: 'granted',
        DENIED: 'denied',
        BLOCKED: 'blocked',
    },
}));

// Mock expo-av
jest.mock('expo-av', () => ({
    Audio: {
        Sound: {
            createAsync: jest.fn().mockResolvedValue({
                sound: {
                    playAsync: jest.fn(),
                    unloadAsync: jest.fn(),
                },
            }),
        },
        setAudioModeAsync: jest.fn(),
    },
}));

// Mock AsyncStorage
jest.mock('@react-native-async-storage/async-storage', () => ({
    setItem: jest.fn(),
    getItem: jest.fn(),
    removeItem: jest.fn(),
    clear: jest.fn(),
}));

// Mock Platform
jest.mock('react-native/Libraries/Utilities/Platform', () => ({
    OS: 'android',
    select: jest.fn((obj) => obj.android),
    Version: 30,
}));

// Silence console errors during tests
global.console = {
    ...console,
    error: jest.fn(),
    warn: jest.fn(),
};
