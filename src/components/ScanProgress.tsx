import React from 'react';
import { StyleSheet, Text, View } from 'react-native';

interface ScanProgressProps {
  progress?: number;
  message?: string;
}

export function ScanProgress({ progress = 0, message = 'Scanning...' }: ScanProgressProps) {
  return (
    <View style={styles.container}>
      <Text style={styles.message}>{message}</Text>
      <View style={styles.progressBar}>
        <View style={[styles.progressFill, { width: `${progress}%` }]} />
      </View>
      <Text style={styles.percent}>{progress}%</Text>
    </View>
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
  message: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  progressBar: {
    height: 8,
    backgroundColor: '#f5f5f5',
    borderRadius: 4,
    overflow: 'hidden',
    marginBottom: 8,
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#000',
  },
  percent: {
    fontSize: 12,
    color: '#999',
    textAlign: 'right',
  },
});
