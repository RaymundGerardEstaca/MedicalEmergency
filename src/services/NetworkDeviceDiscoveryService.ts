/**
 * NetworkDeviceDiscoveryService - LAN scanning for camera discovery
 */

interface DiscoveredDevice {
  ip: string;
  port: number;
  isCamera: boolean;
}

class NetworkDeviceDiscoveryService {
  async scanNetwork(baseIp?: string): Promise<DiscoveredDevice[]> {
    // TODO: Implement network scanning
    return [];
  }

  async checkDevice(ip: string): Promise<DiscoveredDevice | null> {
    // TODO: Implement device check
    return null;
  }
}

export default new NetworkDeviceDiscoveryService();
