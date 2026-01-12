import React from 'react';
import { StyleSheet, Text, View } from 'react-native';

export default function NetworkScanner() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Network Scanner Component</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 16,
    backgroundColor: '#f5f5f5',
    borderRadius: 12,
  },
  title: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#000',
  },
});
