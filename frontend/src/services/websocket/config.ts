import { reactive } from 'vue';

/**
 * WebSocket配置接口
 */
export interface WebSocketConfig {
  heartbeatInterval: number; // 心跳间隔(ms)
  reconnectAttempts: number; // 重连尝试次数
  reconnectInterval: number; // 重连间隔(ms)
  reconnectBackoff: boolean; // 是否使用指数退避策略
  debug: boolean;            // 是否开启调试模式
  enabled: boolean;          // 是否启用WebSocket
}

/**
 * 检查浏览器是否支持WebSocket
 */
export function isWebSocketSupported(): boolean {
  return typeof WebSocket !== 'undefined';
}

/**
 * 检查WebSocket URL是否有效
 */
export function isValidWebSocketUrl(url: string): boolean {
  if (!url) return false;
  return url.startsWith('ws://') || url.startsWith('wss://');
}

/**
 * 默认WebSocket配置
 */
const defaultConfig: WebSocketConfig = {
  heartbeatInterval: 30000,  // 30秒
  reconnectAttempts: 10,     // 增加到10次尝试
  reconnectInterval: 5000,   // 增加到5秒
  reconnectBackoff: true,    // 启用指数退避
  debug: import.meta.env.DEV, // 开发环境开启调试
  enabled: isWebSocketSupported(), // 默认在支持WebSocket的环境中启用
};

/**
 * 全局WebSocket配置对象
 */
export const wsConfig = reactive<WebSocketConfig>({
  ...defaultConfig
});

/**
 * 更新WebSocket配置
 * @param config 配置参数
 */
export function updateWsConfig(config: Partial<WebSocketConfig>): void {
  Object.assign(wsConfig, config);
}

/**
 * 启用或禁用WebSocket
 * @param enabled 是否启用
 */
export function enableWebSocket(enabled: boolean): void {
  wsConfig.enabled = enabled && isWebSocketSupported();
}

/**
 * 从系统设置中加载WebSocket配置
 * @param settings 系统设置对象
 */
export function loadWsConfigFromSettings(settings: Record<string, any>): void {
  updateWsConfig({
    heartbeatInterval: (settings.websocket_heartbeat_interval || 30) * 1000,
    reconnectAttempts: settings.websocket_max_reconnect || 5,
    reconnectInterval: (settings.websocket_reconnect_interval || 3) * 1000,
    enabled: (settings.enable_websocket !== undefined ? settings.enable_websocket : true) && isWebSocketSupported()
  });
}

/**
 * 检查WebSocket环境支持情况
 * 返回一个包含支持信息的对象
 */
export function checkWebSocketSupport(): {
  supported: boolean;
  secure: boolean;
  baseUrlConfigured: boolean;
  baseUrlValid: boolean;
  reason?: string;
} {
  // 检查浏览器支持
  if (!isWebSocketSupported()) {
    return {
      supported: false,
      secure: false,
      baseUrlConfigured: false,
      baseUrlValid: false,
      reason: '当前浏览器不支持WebSocket'
    };
  }
  
  // 检查基础URL - 添加更友好的默认值处理
  let baseUrl = import.meta.env.VITE_WS_BASE_URL;
  
  // 如果没有配置环境变量，尝试使用自动生成的URL
  if (!baseUrl) {
    // 从API URL获取基础URL
    const apiUrl = import.meta.env.VITE_API_BASE_URL || window.location.origin;
    const isSecure = window.location.protocol === 'https:' || apiUrl.startsWith('https://');
    
    // 尝试构建WebSocket URL
    try {
      const urlObj = new URL(apiUrl);
      baseUrl = `${isSecure ? 'wss' : 'ws'}://${urlObj.host}/ws`;
      console.log(`未配置WebSocket URL，自动生成: ${baseUrl}`);
    } catch (e) {
      console.warn('无法从API URL构建WebSocket URL:', e);
    }
  }
  
  const baseUrlConfigured = !!baseUrl;
  const baseUrlValid = isValidWebSocketUrl(baseUrl);
  const secure = baseUrl?.startsWith('wss://') || false;
  
  if (!baseUrlConfigured) {
    return {
      supported: false,
      secure,
      baseUrlConfigured,
      baseUrlValid,
      reason: 'WebSocket基础URL未配置，请检查环境变量VITE_WS_BASE_URL或手动配置'
    };
  }
  
  if (!baseUrlValid) {
    return {
      supported: false,
      secure,
      baseUrlConfigured,
      baseUrlValid,
      reason: `WebSocket基础URL格式无效: ${baseUrl}，请确保以ws://或wss://开头`
    };
  }
  
  return {
    supported: true,
    secure,
    baseUrlConfigured,
    baseUrlValid
  };
}

/**
 * 自动配置WebSocket
 * 检查环境支持并设置合适的配置
 */
export function autoConfigureWebSocket(): { 
  enabled: boolean; 
  supportInfo: ReturnType<typeof checkWebSocketSupport>;
} {
  const supportInfo = checkWebSocketSupport();
  enableWebSocket(supportInfo.supported);
  
  // 如果开发环境且WebSocket未配置正确，输出警告
  if (import.meta.env.DEV && !supportInfo.supported) {
    console.warn(`WebSocket支持检查: ${supportInfo.reason}`);
  }
  
  return { 
    enabled: wsConfig.enabled,
    supportInfo
  };
}

/**
 * 重置WebSocket配置为默认值
 */
export function resetWsConfig(): void {
  Object.assign(wsConfig, defaultConfig);
}

export default wsConfig; 