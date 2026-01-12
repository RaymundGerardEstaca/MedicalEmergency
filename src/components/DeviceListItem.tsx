import React from 'react';
import { StyleSheet, Text, TouchableOpacity } from 'react-native';

export interface ScannedDevice {
  id: string;
  name: string;
  type: 'ble' | 'wifi';
}

interface DeviceListItemProps {
  device: ScannedDevice;
  onPress?: () => void;
}

export function DeviceListItem({ device, onPress }: DeviceListItemProps) {
  return (
    <TouchableOpacity style={styles.container} onPress={onPress}>
      <Text style={styles.name}>{device.name}</Text>
      <Text style={styles.id}>{device.id}</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 16,
    backgroundColor: '#fff',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e5e5e5',
  },
  name: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#000',
    marginBottom: 4,
  },
  id: {
    fontSize: 12,
    color: '#666',
  },
});
