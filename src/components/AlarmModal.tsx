import React from 'react';
import { Modal, StyleSheet, Text, View } from 'react-native';

export default function AlarmModal() {
  return (
    <Modal transparent visible={false}>
      <View style={styles.container}>
        <Text style={styles.title}>Alarm Modal Component</Text>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
  },
});
