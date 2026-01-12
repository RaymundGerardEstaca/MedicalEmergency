/**
 * BLEProvisioningService - Bluetooth Low Energy provisioning for cameras
 */

export interface BLEDevice {
  id: string;
  name: string | null;
  rssi: number | null;
}

class BLEProvisioningService {
  async scanForDevices(): Promise<BLEDevice[]> {
    // TODO: Implement BLE scanning
    return [];
  }

  async connect(deviceId: string): Promise<boolean> {
    // TODO: Implement BLE connection
    return false;
  }

  async provisionWiFi(deviceId: string, ssid: string, password: string): Promise<boolean> {
    // TODO: Implement WiFi provisioning
    return false;
  }
}

export default new BLEProvisioningService();
