import React, { useState, useEffect } from 'react';
import { 
  View, 
  Text, 
  TouchableOpacity, 
  StyleSheet, 
  ScrollView,
  SafeAreaView,
  ActivityIndicator
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { cameraAPI, statsAPI } from '../services/api';

export default function Dashboard() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [cameras, setCameras] = useState([]);
  const [stats, setStats] = useState({
    totalCameras: 0,
    online: 0,
    offline: 0,
    alerts: 0
  });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  const navigation = useNavigation();

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setIsLoading(true);
    setError("");
    
    try {
      const camerasData = await cameraAPI.getCameras();
      const statsData = await statsAPI.getStats();
      
      setCameras(camerasData || []);
      setStats({
        totalCameras: statsData?.totalCameras || 0,
        online: statsData?.online || 0,
        offline: statsData?.offline || 0,
        alerts: statsData?.alerts || 0
      });
    } catch (err) {
      setError(err.message || "Failed to load dashboard data");
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    setMenuOpen(false);
    navigation.replace('Login');
  };

  const handleAddCamera = () => {
    navigation.navigate('DiscoverCameras');
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>My Cameras</Text>
        <View style={styles.menuWrapper}>
          <TouchableOpacity 
            style={styles.menuIcon}
            onPress={() => setMenuOpen(!menuOpen)}
          >
            <Text style={{fontSize: 24, fontWeight: 'bold'}}>⋮</Text>
          </TouchableOpacity>
          {menuOpen && (
            <View style={styles.menuDropdown}>
              <TouchableOpacity onPress={handleLogout} style={styles.menuItem}>
                <Text style={styles.menuItemText}>Logout</Text>
              </TouchableOpacity>
            </View>
          )}
        </View>
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        <View style={styles.statsContainer}>
          <View style={styles.statCard}>
            <Text style={styles.statLabel}>TOTAL CAMERAS</Text>
            <Text style={styles.statValue}>{String(stats.totalCameras).padStart(2, '0')}</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statLabel}>ONLINE</Text>
            <Text style={styles.statValue}>{String(stats.online).padStart(2, '0')}</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statLabel}>OFFLINE</Text>
            <Text style={styles.statValue}>{String(stats.offline).padStart(2, '0')}</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statLabel}>ALERTS</Text>
            <Text style={styles.statValue}>{String(stats.alerts).padStart(2, '0')}</Text>
          </View>
        </View>

        <Text style={styles.sectionTitle}>Your Cameras</Text>

        <View style={styles.camerasContainer}>
          {error ? <Text style={styles.errorText}>{error}</Text> : null}
          
          {isLoading ? (
            <View style={styles.emptyState}>
              <ActivityIndicator size="large" color="#007AFF" />
              <Text style={styles.emptyTitle}>Loading...</Text>
            </View>
          ) : cameras.length === 0 ? (
            <View style={styles.emptyState}>
              <Text style={styles.emptyIcon}>📷</Text>
              <Text style={styles.emptyTitle}>No cameras yet</Text>
              <Text style={styles.emptyText}>Add your first camera to start monitoring</Text>
              <TouchableOpacity style={styles.addBtn} onPress={handleAddCamera}>
                <Text style={styles.addBtnText}>Add Your First Camera</Text>
              </TouchableOpacity>
            </View>
          ) : (
            <View style={styles.camerasList}>
              {cameras.map((camera, index) => (
                <View key={index} style={styles.cameraCard}>
                  <Text style={styles.cameraName}>{camera.name}</Text>
                  <Text style={[
                      styles.cameraStatus, 
                      { color: camera.status === 'Online' ? '#4caf50' : '#d32f2f' }
                  ]}>
                    {camera.status}
                  </Text>
                </View>
              ))}
              
              <TouchableOpacity style={styles.secondaryAddBtn} onPress={handleAddCamera}>
                <Text style={styles.secondaryAddBtnText}>+ Add Another Camera</Text>
              </TouchableOpacity>
            </View>
          )}
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
    padding: 20,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
    zIndex: 10,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  menuWrapper: {
    position: 'relative',
  },
  menuIcon: {
    padding: 8,
  },
  menuDropdown: {
    position: 'absolute',
    top: 40,
    right: 0,
    backgroundColor: 'white',
    borderRadius: 8,
    padding: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
    zIndex: 100,
  },
  menuItem: {
    paddingVertical: 10,
    paddingHorizontal: 16,
  },
  menuItemText: {
    fontSize: 16,
    color: '#d32f2f',
  },
  scrollContent: {
    padding: 20,
  },
  statsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: 24,
  },
  statCard: {
    width: '48%',
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 8,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    fontWeight: '600',
    marginBottom: 8,
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  camerasContainer: {
    flex: 1,
  },
  errorText: {
    color: '#d32f2f',
    textAlign: 'center',
    marginBottom: 12,
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
  addBtn: {
    backgroundColor: '#007AFF',
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
  },
  addBtnText: {
    color: 'white',
    fontWeight: '600',
    fontSize: 16,
  },
  camerasList: {
    gap: 16,
  },
  cameraCard: {
    backgroundColor: 'white',
    borderRadius: 8,
    padding: 20,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
    marginBottom: 12,
  },
  cameraName: {
    fontSize: 18,
    fontWeight: '600',
  },
  cameraStatus: {
    fontSize: 14,
    fontWeight: '500',
  },
  secondaryAddBtn: {
    padding: 16,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#007AFF',
    borderRadius: 8,
    borderStyle: 'dashed',
    marginTop: 8,
  },
  secondaryAddBtnText: {
    color: '#007AFF',
    fontWeight: '600',
  }
});
