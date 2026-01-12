import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { StatusBar } from 'expo-status-bar';
import React from 'react';
import CameraConfigScreen from './src/screens/CameraConfigScreen';
import DeviceDiscoveryScreen from './src/screens/DeviceDiscoveryScreen';
import DevicesListScreen from './src/screens/DevicesListScreen';
import LoginScreen from './src/screens/LoginScreen';
import SoftAPProvisioningScreen from './src/screens/SoftAPProvisioningScreen';
import StreamViewerScreen from './src/screens/StreamViewerScreen';
import WiFiProvisioningScreen from './src/screens/WiFiProvisioningScreen';
import { BLEDevice } from './src/services/BLEProvisioningService';
import { CCTVDevice } from './src/services/DeviceStorageService';
import { CameraConfig } from './src/types';

export type RootStackParamList = {
    Login: undefined;
    DevicesList: undefined;
    DeviceDiscovery: undefined;
    WiFiProvisioning: { device: BLEDevice };
    SoftAPProvisioning: { targetSSID?: string };
    CameraConfig: { device?: BLEDevice; existingConfig?: CameraConfig };
    StreamViewer: { device?: CCTVDevice; cameraConfig?: CameraConfig };
};

const Stack = createStackNavigator<RootStackParamList>();

export default function App() {
    return (
        <NavigationContainer>
            <StatusBar style="light" />
            <Stack.Navigator
                initialRouteName="Login"
                screenOptions={{
                    headerStyle: {
                        backgroundColor: '#000',
                    },
                    headerTintColor: '#fff',
                    headerTitleStyle: {
                        fontWeight: 'bold',
                    },
                    cardStyle: {
                        backgroundColor: '#fff',
                    },
                }}
            >
                {/* Auth Flow - No Header */}
                <Stack.Screen
                    name="Login"
                    component={LoginScreen}
                    options={{ headerShown: false }}
                />

                {/* Main App Flow */}
                <Stack.Screen
                    name="DevicesList"
                    component={DevicesListScreen}
                    options={{ title: 'My Cameras' }}
                />
                <Stack.Screen
                    name="DeviceDiscovery"
                    component={DeviceDiscoveryScreen}
                    options={{ title: 'Discover Cameras' }}
                />
                <Stack.Screen
                    name="WiFiProvisioning"
                    component={WiFiProvisioningScreen}
                    options={{ title: 'Configure via BLE' }}
                />
                <Stack.Screen
                    name="SoftAPProvisioning"
                    component={SoftAPProvisioningScreen}
                    options={{ title: 'WiFi Hotspot Method' }}
                />
                <Stack.Screen
                    name="CameraConfig"
                    component={CameraConfigScreen}
                    options={{ title: 'Camera Settings' }}
                />
                <Stack.Screen
                    name="StreamViewer"
                    component={StreamViewerScreen}
                    options={{ title: 'Live Stream' }}
                />
            </Stack.Navigator>
        </NavigationContainer>
    );
}
