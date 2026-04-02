import React, { useState } from 'react';
import { 
  View, 
  Text, 
  TouchableOpacity, 
  StyleSheet, 
  SafeAreaView,
  ScrollView,
  ActivityIndicator
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { discoveryAPI } from '../services/api';

export default function DiscoverCameras() {
  const [scanMode, setScanMode] = useState("bluetooth");
  const [discoveredDevices, setDiscoveredDevices] = useState([]);
  const [isScanning, setIsScanning] = useState(false);
  const [error, setError] = useState("");

  const navigation = useNavigation();

  const pairingSteps = [
    "Power on your camera device",
    "Press and hold the pairing button for 5 seconds",
    "Wait for the LED to blink rapidly",
    "Select the device from the list above"
  ];

  const handleScan = async () => {
    setIsScanning(true);
    setError("");
    setDiscoveredDevices([]);
    
    try {
      const devices = await discoveryAPI.scanDevices(scanMode);
      setDiscoveredDevices(devices || []);
    } catch (err) {
      setError(err.message || "Scan failed");
    } finally {
      setIsScanning(false);
    }
  };

  const handlePair = async (device) => {
    try {
      await discoveryAPI.pairDevice(device.id, scanMode);
      console.log(`Successfully paired with ${device.name}`);
      navigation.goBack();
    } catch (err) {
      setError(err.message || "Pairing failed");
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity style={styles.backBtn} onPress={() => navigation.goBack()}>
          <Text style={styles.backBtnText}>← Back</Text>
        </TouchableOpacity>
        <Text style={styles.title}>Discover Cameras</Text>
        <View style={{ width: 60 }} />
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        <Text style={styles.subtitle}>Scanning for available devices via {scanMode === 'bluetooth' ? 'Bluetooth' : 'WiFi hotspot'}</Text>

        {error ? <Text style={styles.errorText}>{error}</Text> : null}

        <View style={styles.modeToggle}>
          <TouchableOpacity 
            style={[styles.modeBtn, scanMode === "bluetooth" && styles.modeBtnActive]}
            onPress={() => setScanMode("bluetooth")}
            disabled={isScanning}
          >
            <Text style={[styles.modeBtnText, scanMode === "bluetooth" && styles.modeBtnTextActive]}>Bluetooth</Text>
          </TouchableOpacity>
          <TouchableOpacity 
            style={[styles.modeBtn, scanMode === "wifi" && styles.modeBtnActive]}
            onPress={() => setScanMode("wifi")}
            disabled={isScanning}
          >
            <Text style={[styles.modeBtnText, scanMode === "wifi" && styles.modeBtnTextActive]}>WiFi Hotspot</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Discovered Devices ({discoveredDevices.length})</Text>
            <TouchableOpacity onPress={handleScan} disabled={isScanning}>
              <Text style={styles.scanAgainTxt}>{isScanning ? "Scanning..." : "Scan Again"}</Text>
            </TouchableOpacity>
          </View>

          {discoveredDevices.length === 0 ? (
            <View style={styles.emptyState}>
              {isScanning ? (
                <>
                  <ActivityIndicator size="large" color="#007AFF" style={{marginBottom: 16}} />
                  <Text style={styles.emptyTitle}>Scanning...</Text>
                </>
              ) : (
                <>
                  <Text style={styles.emptyIcon}>📡</Text>
                  <Text style={styles.emptyTitle}>No devices found</Text>
                  <Text style={styles.emptyText}>Ensure your camera is in pairing mode</Text>
                  <TouchableOpacity style={styles.retryBtn} onPress={handleScan}>
                    <Text style={styles.retryBtnText}>Retry Scan</Text>
                  </TouchableOpacity>
                </>
              )}
            </View>
          ) : (
            <View style={styles.devicesList}>
              {discoveredDevices.map((device, index) => (
                <View key={index} style={styles.deviceItem}>
                  <View style={styles.deviceInfo}>
                    <Text style={styles.deviceName}>{device.name}</Text>
                    <Text style={styles.deviceSignal}>{device.signal}</Text>
                  </View>
                  <TouchableOpacity 
                    style={styles.pairBtn}
                    onPress={() => handlePair(device)}
                  >
                    <Text style={styles.pairBtnText}>Pair</Text>
                  </TouchableOpacity>
                </View>
              ))}
            </View>
          )}
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Pairing Instructions</Text>
          <View style={styles.instructionsContainer}>
            {pairingSteps.map((step, index) => (
              <View key={index} style={styles.instructionItem}>
                <View style={styles.instructionNumberContainer}>
                  <Text style={styles.instructionNumber}>{index + 1}</Text>
                </View>
                <Text style={styles.instructionText}>{step}</Text>
              </View>
            ))}
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  backBtn: {
    width: 60,
  },
  backBtnText: {
    color: '#007AFF',
    fontSize: 16,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  scrollContent: {
    padding: 20,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 24,
  },
  errorText: {
    color: '#d32f2f',
    textAlign: 'center',
    marginBottom: 16,
  },
  modeToggle: {
    flexDirection: 'row',
    backgroundColor: '#e0e0e0',
    borderRadius: 8,
    padding: 4,
    marginBottom: 32,
  },
  modeBtn: {
    flex: 1,
    paddingVertical: 10,
    alignItems: 'center',
    borderRadius: 6,
  },
  modeBtnActive: {
    backgroundColor: 'white',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  modeBtnText: {
    color: '#666',
    fontWeight: '500',
  },
  modeBtnTextActive: {
    color: '#000',
    fontWeight: '600',
  },
  section: {
    marginBottom: 32,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  scanAgainTxt: {
    color: '#007AFF',
    fontWeight: '600',
  },
  emptyState: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 32,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  emptyIcon: {
    fontSize: 48,
    marginBottom: 16,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: '600',
    marginBottom: 8,
  },
  emptyText: {
    color: '#666',
    textAlign: 'center',
    marginBottom: 24,
  },
  retryBtn: {
    backgroundColor: '#007AFF',
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
  },
  retryBtnText: {
    color: 'white',
    fontWeight: '600',
    fontSize: 16,
  },
  devicesList: {
    backgroundColor: 'white',
    borderRadius: 12,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  deviceItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  deviceInfo: {
    flex: 1,
  },
  deviceName: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 4,
  },
  deviceSignal: {
    fontSize: 12,
    color: '#666',
  },
  pairBtn: {
    backgroundColor: '#4caf50',
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 20,
  },
  pairBtnText: {
    color: 'white',
    fontWeight: '600',
  },
  instructionsContainer: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
  },
  instructionItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  instructionNumberContainer: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: '#e3f2fd',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  instructionNumber: {
    color: '#007AFF',
    fontWeight: 'bold',
  },
  instructionText: {
    flex: 1,
    fontSize: 15,
    color: '#333',
    lineHeight: 22,
  }
});
