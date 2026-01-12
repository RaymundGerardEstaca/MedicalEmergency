/**
 * SoftAPProvisioningService - WiFi provisioning via camera hotspot
 */

export interface SoftAPProvisioningStatus {
  stage: 'idle' | 'connecting' | 'sending' | 'success' | 'failed';
  message: string;
  progress: number;
}

class SoftAPProvisioningService {
  async isConnectedToCameraAP(): Promise<{ connected: boolean; ssid: string | null }> {
    // TODO: Implement camera AP detection
    return { connected: false, ssid: null };
  }

  async provisionViaSoftAP(ssid: string, password: string): Promise<boolean> {
    // TODO: Implement SoftAP provisioning
    return false;
  }
}

export default new SoftAPProvisioningService();
