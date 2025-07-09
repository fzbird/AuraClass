import http from '../http';
import { loadWsConfigFromSettings, updateWsConfig } from '../websocket/config';

/**
 * 系统设置类型定义
 */
export interface SystemSettings {
  system_name: string;
  logo_url: string;
  enable_notifications: boolean;
  enable_ai_assistant: boolean;
  enable_websocket: boolean;
  max_quant_score: number;
  min_quant_score: number;
  quant_categories: string[];
  websocket_heartbeat_interval?: number;
  websocket_max_reconnect?: number;
  websocket_reconnect_interval?: number;
}

// 默认系统设置配置
const DEFAULT_SYSTEM_SETTINGS: SystemSettings = {
  system_name: 'AuraClass 班级量化管理系统',
  logo_url: '/logo.png',
  enable_notifications: true,
  enable_ai_assistant: true,
  enable_websocket: false,
  max_quant_score: 5,
  min_quant_score: -5,
  quant_categories: ['学习', '纪律', '卫生', '德育'],
  websocket_heartbeat_interval: 30000,
  websocket_max_reconnect: 5,
  websocket_reconnect_interval: 5000
};

/**
 * 获取系统设置
 */
export async function getSystemSettings() {
  try {
    await http.get('/health/health');
    
    // 返回默认设置
    return { data: DEFAULT_SYSTEM_SETTINGS };
  } catch (error) {
    console.warn('Failed to connect to backend, using default settings:', error);
    return { data: DEFAULT_SYSTEM_SETTINGS };
  }
}

/**
 * 更新系统设置
 * 注意：后端没有提供/settings端点，此处返回传入的设置
 */
export async function updateSystemSettings(settings: SystemSettings) {
  console.warn('Settings update API not available, returning provided settings');
  return { data: settings };
}

/**
 * 上传系统Logo
 * 注意：后端没有提供/settings/logo端点，此处返回默认Logo
 */
export async function uploadSystemLogo(formData: FormData) {
  console.warn('Logo upload API not available, returning default logo');
  return { data: { logo_url: '/logo.png' } };
}

/**
 * 初始化应用设置
 * 使用默认系统设置
 */
export async function initAppSettings() {
  try {
    const response = await getSystemSettings();
    if (response && response.data) {
      // 确保WebSocket初始状态为禁用
      response.data.enable_websocket = false;
      // 加载WebSocket配置
      loadWsConfigFromSettings(response.data);
      return response.data;
    }
  } catch (error) {
    console.error('Failed to initialize app settings:', error);
  }
  
  // 使用默认配置
  console.info('Using default app settings');
  // 确保WebSocket初始状态为禁用
  DEFAULT_SYSTEM_SETTINGS.enable_websocket = false;
  loadWsConfigFromSettings(DEFAULT_SYSTEM_SETTINGS);
  return DEFAULT_SYSTEM_SETTINGS;
}

/**
 * 检查WebSocket服务是否可用
 * @returns {Promise<boolean>} WebSocket服务是否可用
 */
export async function checkWebSocketAvailability(): Promise<boolean> {
  try {
    // 创建一个WebSocket连接尝试，设置较短的超时时间
    return await new Promise((resolve) => {
      const baseUrl = import.meta.env.VITE_WS_BASE_URL;
      const testSocket = new WebSocket(`${baseUrl}/health`);
      
      // 设置5秒超时
      const timeout = setTimeout(() => {
        testSocket.close();
        resolve(false);
      }, 5000);
      
      testSocket.onopen = () => {
        clearTimeout(timeout);
        testSocket.close();
        resolve(true);
      };
      
      testSocket.onerror = () => {
        clearTimeout(timeout);
        resolve(false);
      };
    });
  } catch (error) {
    console.warn('Failed to check WebSocket availability:', error);
    return false;
  }
}

/**
 * 启用或禁用WebSocket功能
 * @param {boolean} enable 是否启用WebSocket
 * @returns {Promise<boolean>} 操作是否成功
 */
export async function toggleWebSocketFeature(enable: boolean): Promise<boolean> {
  try {
    if (enable) {
      // 检查WebSocket服务是否可用
      const available = await checkWebSocketAvailability();
      if (!available) {
        console.warn('WebSocket service is not available');
        return false;
      }
    }
    
    // 更新WebSocket配置
    updateWsConfig({ enabled: enable });
    return true;
  } catch (error) {
    console.error('Failed to toggle WebSocket feature:', error);
    return false;
  }
} 