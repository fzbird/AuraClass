import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { WebSocketConfig } from '@/services/websocket/config';
import wsConfig from '@/services/websocket/config';

export const useWebSocketStore = defineStore('websocket', () => {
  // 连接状态
  const isConnected = ref(false);
  const isConnecting = ref(false);
  const connectionError = ref<string | null>(null);
  const endpoint = ref<string | null>(null);
  const lastConnectedTime = ref<number | null>(null);
  
  // 统计数据
  const reconnectCount = ref(0);
  const messageCount = ref(0);
  
  // 配置
  const config = ref<WebSocketConfig>(wsConfig);
  
  // 更新连接状态
  function setConnectionStatus(status: boolean) {
    isConnected.value = status;
    if (status) {
      connectionError.value = null;
      lastConnectedTime.value = Date.now();
    }
  }
  
  // 开始连接
  function setConnecting(connecting: boolean) {
    isConnecting.value = connecting;
  }
  
  // 设置连接错误
  function setConnectionError(error: string | null) {
    connectionError.value = error;
    if (error) {
      isConnected.value = false;
    }
  }
  
  // 设置WebSocket端点
  function setEndpoint(url: string) {
    endpoint.value = url;
  }
  
  // 增加重连计数
  function incrementReconnectCount() {
    reconnectCount.value++;
  }
  
  // 重置重连计数
  function resetReconnectCount() {
    reconnectCount.value = 0;
  }
  
  // 增加消息计数
  function incrementMessageCount() {
    messageCount.value++;
  }
  
  // 更新配置
  function updateConfig(newConfig: Partial<WebSocketConfig>) {
    config.value = {
      ...config.value,
      ...newConfig
    };
  }
  
  // 重置所有状态
  function reset() {
    isConnected.value = false;
    isConnecting.value = false;
    connectionError.value = null;
    reconnectCount.value = 0;
    messageCount.value = 0;
  }
  
  return {
    // 状态
    isConnected,
    isConnecting,
    connectionError,
    endpoint,
    lastConnectedTime,
    reconnectCount,
    messageCount,
    config,
    
    // 方法
    setConnectionStatus,
    setConnecting,
    setConnectionError,
    setEndpoint,
    incrementReconnectCount,
    resetReconnectCount,
    incrementMessageCount,
    updateConfig,
    reset
  };
}); 