/**
 * LoggerService - Centralized logging for the app
 */

type LogLevel = 'debug' | 'info' | 'warn' | 'error';

class LoggerService {
  debug(tag: string, message: string, data?: any): void {
    console.log(`[DEBUG] ${tag}: ${message}`, data);
  }

  info(tag: string, message: string, data?: any): void {
    console.log(`[INFO] ${tag}: ${message}`, data);
  }

  warn(tag: string, message: string, data?: any): void {
    console.warn(`[WARN] ${tag}: ${message}`, data);
  }

  error(tag: string, message: string, data?: any): void {
    console.error(`[ERROR] ${tag}: ${message}`, data);
  }
}

export default new LoggerService();
