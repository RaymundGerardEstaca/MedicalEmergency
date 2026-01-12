/**
 * WiFiDetectionService Tests - Basic starter tests
 */

import WiFiDetectionService from '../WiFiDetectionService';

describe('WiFiDetectionService', () => {
  describe('getCurrentSSID', () => {
    it('should return null by default', async () => {
      const ssid = await WiFiDetectionService.getCurrentSSID();
      expect(ssid).toBeNull();
    });
  });

  describe('getCurrentFrequency', () => {
    it('should return null by default', async () => {
      const frequency = await WiFiDetectionService.getCurrentFrequency();
      expect(frequency).toBeNull();
    });
  });

  describe('validateWiFiFor2_4GHz', () => {
    it('should return false by default', async () => {
      const result = await WiFiDetectionService.validateWiFiFor2_4GHz();
      expect(result.is2_4GHz).toBe(false);
    });

    it('should handle SSID parameter', async () => {
      const result = await WiFiDetectionService.validateWiFiFor2_4GHz('TestNetwork');
      expect(result.is2_4GHz).toBe(false);
    });
  });

  describe('getConnectionInfo', () => {
    it('should return null values by default', async () => {
      const info = await WiFiDetectionService.getConnectionInfo();
      expect(info.ssid).toBeNull();
      expect(info.frequency).toBeNull();
      expect(info.is2_4GHz).toBeNull();
    });
  });
});
