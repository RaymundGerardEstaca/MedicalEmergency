/**
 * SmartConfigService - WiFi provisioning via SmartConfig/ESPTouch
 */

export interface SmartConfigParams {
  ssid: string;
  password: string;
  timeoutMs?: number;
}

export interface SmartConfigResult {
  deviceIp?: string;
  success: boolean;
}

class SmartConfigService {
  async configure(params: SmartConfigParams): Promise<SmartConfigResult> {
    // TODO: Implement SmartConfig provisioning
    return {
      success: false,
      deviceIp: undefined,
    };
  }
}

export default new SmartConfigService();
