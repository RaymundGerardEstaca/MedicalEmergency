/**
 * BackendAPIService - Handles communication with backend server
 */

class BackendAPIService {
  private baseUrl: string = 'http://localhost:8000';

  async checkHealth(): Promise<{ status: string }> {
    // TODO: Implement health check
    return { status: 'ok' };
  }

  async getDevices(): Promise<any[]> {
    // TODO: Implement get devices
    return [];
  }
}

export default new BackendAPIService();
