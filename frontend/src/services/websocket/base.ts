import { ref, watch } from 'vue';
import { useUserStore } from '@/stores/user';
import { useWebSocketStore } from '@/stores/websocket';
import wsConfig from './config';

/**
 * 基础WebSocket服务类
 * 提供通用的WebSocket连接管理、重连机制和状态监控
 */
export function useBaseWebSocket(endpoint: string, options = {}) {
  // 默认配置
  const defaultOptions = {
    reconnectInterval: wsConfig.reconnectInterval,
    reconnectAttempts: wsConfig.reconnectAttempts,
    reconnectBackoff: wsConfig.reconnectBackoff,
    heartbeatInterval: wsConfig.heartbeatInterval,
    heartbeatMessage: { type: 'ping' },
    debug: wsConfig.debug
  };

  // 合并配置
  const config = { ...defaultOptions, ...options };
  
  // 状态管理
  const socket = ref<WebSocket | null>(null);
  const isConnected = ref(false);
  const isConnecting = ref(false);
  const connectionError = ref<string | null>(null);
  const reconnectCount = ref(0);
  const reconnectTimer = ref<number | null>(null);
  const heartbeatTimer = ref<number | null>(null);
  const messageCount = ref(0);
  
  const userStore = useUserStore();
  const wsStore = useWebSocketStore();
  
  // 监听用户登录状态和WebSocket启用状态
  watch(() => [userStore.isLoggedIn, wsConfig.enabled], ([loggedIn, enabled]) => {
    if (loggedIn && enabled && !isConnected.value && !isConnecting.value) {
      connect();
    } else if ((!loggedIn || !enabled) && (isConnected.value || isConnecting.value)) {
      disconnect();
    }
  });
  
  /**
   * 构建WebSocket URL
   */
  const buildWebSocketUrl = () => {
    const token = userStore.token;
    const baseUrl = import.meta.env.VITE_WS_BASE_URL;
    const userId = userStore.user?.id;
    
    if (!token || !userId) {
      throw new Error("用户未登录或身份信息缺失");
    }
    
    // 确保baseUrl是以ws://或wss://开头的有效WebSocket URL
    if (!baseUrl) {
      throw new Error("WebSocket基础URL未配置");
    }
    
    if (!baseUrl.startsWith('ws://') && !baseUrl.startsWith('wss://')) {
      throw new Error(`WebSocket基础URL格式错误: ${baseUrl}`);
    }
    
    // 构造WebSocket URL，确保路径格式正确
    let path = endpoint;
    if (!path.startsWith('/')) {
      path = '/' + path;
    }
    
    // 确保路径中的用户ID被正确替换
    path = path.replace('{userId}', userId.toString());
    
    // 移除baseUrl结尾的斜杠(如果有)，以避免双斜杠
    const normalizedBaseUrl = baseUrl.endsWith('/') 
      ? baseUrl.slice(0, -1) 
      : baseUrl;
    
    return `${normalizedBaseUrl}${path}/${userId}?token=${encodeURIComponent(token)}`;
  };
  
  /**
   * 建立WebSocket连接
   */
  const connect = () => {
    if (isConnected.value || isConnecting.value) return;
    
    try {
      isConnecting.value = true;
      connectionError.value = null;
      
      // 更新全局WebSocket状态
      wsStore.setConnecting(true);
      wsStore.setConnectionError(null);
      
      // 构建WebSocket URL
      let wsUrl;
      try {
        wsUrl = buildWebSocketUrl();
        // 设置WebSocket端点
        wsStore.setEndpoint(wsUrl);
      } catch (urlError) {
        const error = `WebSocket URL构建失败: ${urlError instanceof Error ? urlError.message : String(urlError)}`;
        connectionError.value = error;
        wsStore.setConnectionError(error);
        isConnecting.value = false;
        wsStore.setConnecting(false);
        logDebug(error);
        return;
      }
      
      logDebug(`正在连接到 ${wsUrl}`);
      console.log(`尝试建立WebSocket连接: ${wsUrl}`);
      
      // 创建WebSocket实例
      try {
        socket.value = new WebSocket(wsUrl);
      } catch (wsError) {
        const error = `WebSocket实例创建失败: ${wsError instanceof Error ? wsError.message : String(wsError)}`;
        connectionError.value = error;
        wsStore.setConnectionError(error);
        isConnecting.value = false;
        wsStore.setConnecting(false);
        logDebug(error);
        return;
      }
      
      // 连接打开
      socket.value.onopen = () => {
        isConnected.value = true;
        isConnecting.value = false;
        reconnectCount.value = 0;
        connectionError.value = null;
        
        // 更新全局WebSocket状态
        wsStore.setConnectionStatus(true);
        wsStore.setConnecting(false);
        wsStore.resetReconnectCount();
        
        logDebug('WebSocket连接已建立');
        console.log('WebSocket连接已成功建立');
        
        // 开始心跳
        startHeartbeat();
      };
      
      // 连接关闭
      socket.value.onclose = (event) => {
        isConnected.value = false;
        isConnecting.value = false;
        wsStore.setConnectionStatus(false);
        wsStore.setConnecting(false);
        
        let closeReason = '';
        // 分析关闭代码
        switch (event.code) {
          case 1000:
            closeReason = `正常关闭${event.reason ? ': ' + event.reason : ''}`;
            break;
          case 1001:
            closeReason = '端点离开';
            break;
          case 1002:
            closeReason = '协议错误';
            break;
          case 1003:
            closeReason = '不支持的数据';
            break;
          case 1005:
            closeReason = '无状态码';
            break;
          case 1006:
            closeReason = '异常关闭';
            break;
          case 1007:
            closeReason = '无效的数据';
            break;
          case 1008:
            closeReason = `策略违规${event.reason ? ': ' + event.reason : ''}`;
            break;
          case 1009:
            closeReason = '消息过大';
            break;
          case 1010:
            closeReason = '需要扩展';
            break;
          case 1011:
            closeReason = '内部错误';
            break;
          case 1012:
            closeReason = '服务重启';
            break;
          case 1013:
            closeReason = '服务过载';
            break;
          case 1015:
            closeReason = 'TLS握手失败';
            break;
          default:
            closeReason = `未知原因 (${event.code})${event.reason ? ': ' + event.reason : ''}`;
        }
        
        // 设置错误信息
        if (event.code !== 1000 || event.reason?.includes("unauthorized")) {
          connectionError.value = `WebSocket连接已关闭: ${closeReason}`;
          wsStore.setConnectionError(connectionError.value);
        }
        
        // 判断是否需要重连
        if (wsConfig.enabled) {
          // 检查是否是因为授权问题关闭的连接
          if (event.code === 1000 && event.reason && event.reason.includes("unauthorized")) {
            // 授权问题不尝试重连
            const errorMsg = `WebSocket连接已关闭: 授权失败，请重新登录`;
            connectionError.value = errorMsg;
            wsStore.setConnectionError(errorMsg);
            logDebug(errorMsg);
          } else if (event.code === 1000 && event.reason === "正常关闭") {
            // 主动关闭，不自动重连
            logDebug('WebSocket已正常关闭，不自动重连');
          } else {
            // 意外关闭，尝试重连
            logDebug(`WebSocket连接已关闭: ${closeReason}，将尝试重连`);
            scheduleReconnect();
          }
        } else {
          logDebug(`WebSocket连接已关闭: ${closeReason}`);
        }
        
        // 清理心跳
        stopHeartbeat();
      };
      
      // 连接错误
      socket.value.onerror = (event) => {
        isConnecting.value = false;
        
        // 尝试获取更详细的错误信息
        let errorDetails = '';
        try {
          // 检查网络连接
          if (!navigator.onLine) {
            errorDetails = '，网络连接已断开';
          } 
          // 检查URL是否正确
          else if (wsUrl.includes('undefined') || wsUrl.includes('null')) {
            errorDetails = '，URL包含无效值';
          }
          // 检查后端可能性
          else {
            errorDetails = '，可能是后端服务未启动或不可达';
          }
        } catch (e) {
          // 忽略错误分析错误
        }
        
        const errorMsg = `WebSocket连接失败${errorDetails}`;
        connectionError.value = errorMsg;
        wsStore.setConnectionError(errorMsg);
        wsStore.setConnecting(false);
        
        console.error('WebSocket连接错误:', event);
        logDebug('WebSocket连接错误详情:', errorMsg);
        
        // 尝试自动重连
        scheduleReconnect();
      };
      
      // 接收消息
      socket.value.onmessage = (event) => {
        // 增加消息计数
        messageCount.value++;
        wsStore.incrementMessageCount();
        
        // 保存原始消息 
        const rawData = event.data;
        
        try {
          // 尝试解析JSON
          const data = JSON.parse(rawData);
          
          // 处理心跳响应
          if (data.type === 'pong') {
            logDebug('收到心跳响应');
            return;
          }
          
          // 检查常见错误格式
          if (data.error && typeof data.error === 'string') {
            // 检查是否包含datetime序列化错误
            if (data.error.includes('datetime is not JSON serializable')) {
              logDebug('收到datetime序列化错误');
              // 创建修复后的错误响应
              const fixedResponse = {
                type: 'error',
                data: {
                  error: 'datetime_serialization_error',
                  response: '后端数据格式错误 (datetime对象无法序列化)，请联系管理员修复此问题。',
                  processing_time: 0,
                  query_id: null,
                  details: {
                    original_error: data.error,
                    suggestion: '请检查后端datetime对象序列化方式'
                  }
                }
              };
              
              // 传递修复后的消息
              if (socket.value?.onmessage) {
                try {
                  // 创建一个模拟的消息事件
                  const mockEvent = new MessageEvent('message', {
                    data: JSON.stringify(fixedResponse)
                  });
                  // 直接调用onmessage处理函数
                  socket.value.onmessage(mockEvent);
                } catch (e) {
                  console.error('无法分发修复后的错误响应:', e);
                }
              }
              return;
            }
          }
        } catch (e) {
          // 非JSON消息或解析错误
          logDebug('收到非JSON消息或解析错误:', e);
          
          // 检查原始数据是否包含常见错误信息
          const errorText = typeof rawData === 'string' ? rawData : String(rawData);
          
          // 检查各种可能的序列化错误模式
          if (errorText.includes('datetime is not JSON serializable') || 
              errorText.includes('Object of type datetime')) {
            logDebug('检测到datetime序列化错误');
            
            // 创建一个友好的错误响应
            const errorResponse = {
              type: 'response',
              data: {
                response: '由于后端数据格式问题，无法显示完整回复。请联系管理员修复datetime序列化问题。',
                error: 'datetime_serialization_error',
                query_id: '',
                processing_time: 0,
                details: {
                  original_error: errorText
                }
              }
            };
            
            // 手动分发事件
            try {
              const mockEvent = new MessageEvent('message', {
                data: JSON.stringify(errorResponse)
              });
              
              // 确保事件能被所有监听器接收
              if (socket.value?.onmessage) {
                // 直接调用onmessage处理函数
                socket.value.onmessage(mockEvent);
              }
            } catch (dispatchError) {
              console.error('无法分发模拟错误响应:', dispatchError);
            }
          }
        }
      };
      
    } catch (error) {
      isConnecting.value = false;
      const errorMsg = `连接失败: ${error instanceof Error ? error.message : String(error)}`;
      connectionError.value = errorMsg;
      wsStore.setConnectionError(errorMsg);
      wsStore.setConnecting(false);
      console.error('WebSocket连接错误:', error);
      logDebug('连接出错:', error);
    }
  };
  
  /**
   * 断开WebSocket连接
   */
  const disconnect = () => {
    // 取消所有重连和心跳
    if (reconnectTimer.value) {
      window.clearTimeout(reconnectTimer.value);
      reconnectTimer.value = null;
    }
    
    stopHeartbeat();
    
    // 关闭连接
    if (socket.value) {
      const readyState = socket.value.readyState;
      if (readyState === WebSocket.OPEN || readyState === WebSocket.CONNECTING) {
        try {
          socket.value.close(1000, "正常关闭");
        } catch (error) {
          logDebug('关闭连接出错:', error);
        }
      }
    }
    
    socket.value = null;
    isConnected.value = false;
    isConnecting.value = false;
    
    // 更新全局WebSocket状态
    wsStore.setConnectionStatus(false);
    wsStore.setConnecting(false);
  };
  
  /**
   * 手动重新连接
   */
  const reconnect = () => {
    // 先断开当前连接
    disconnect();
    // 重置重连计数
    reconnectCount.value = 0;
    // 增加全局重连计数
    wsStore.incrementReconnectCount();
    // 立即尝试重连
    connect();
  };
  
  /**
   * 安排重连
   */
  const scheduleReconnect = () => {
    if (reconnectTimer.value) {
      window.clearTimeout(reconnectTimer.value);
    }
    
    // 超过最大重连次数
    if (reconnectCount.value >= config.reconnectAttempts) {
      logDebug(`已达到最大重连次数(${config.reconnectAttempts})，停止重连`);
      return;
    }
    
    // 计算重连延迟
    let delay = config.reconnectInterval;
    if (config.reconnectBackoff) {
      // 使用指数退避策略: 基础时间 * (1.5 ^ 重试次数)
      delay = config.reconnectInterval * Math.pow(1.5, reconnectCount.value);
    }
    
    logDebug(`计划在 ${delay}ms 后重连，当前尝试次数: ${reconnectCount.value + 1}`);
    
    // 设置重连定时器
    reconnectTimer.value = window.setTimeout(() => {
      reconnectCount.value++;
      // 增加全局重连计数
      wsStore.incrementReconnectCount();
      connect();
    }, delay);
  };
  
  /**
   * 发送消息
   */
  const send = (data: any) => {
    if (socket.value && socket.value.readyState === WebSocket.OPEN) {
      try {
        const message = typeof data === 'string' ? data : JSON.stringify(data);
        socket.value.send(message);
        return true;
      } catch (error) {
        logDebug('发送消息出错:', error);
        return false;
      }
    } else {
      logDebug('WebSocket未连接，无法发送消息');
      return false;
    }
  };
  
  /**
   * 开始心跳检测
   */
  const startHeartbeat = () => {
    if (!config.heartbeatInterval) return;
    
    stopHeartbeat();
    
    heartbeatTimer.value = window.setInterval(() => {
      if (isConnected.value) {
        send(config.heartbeatMessage);
        logDebug('发送心跳');
      }
    }, config.heartbeatInterval);
  };
  
  /**
   * 停止心跳检测
   */
  const stopHeartbeat = () => {
    if (heartbeatTimer.value) {
      window.clearInterval(heartbeatTimer.value);
      heartbeatTimer.value = null;
    }
  };
  
  /**
   * 调试日志
   */
  const logDebug = (message: string, ...args: any[]) => {
    if (config.debug) {
      console.log(`[WebSocket:${endpoint}] ${message}`, ...args);
    }
  };
  
  // 不再自动连接，改为由用户手动启用WebSocket后才连接
  
  return {
    socket,
    isConnected,
    isConnecting,
    connectionError,
    connect,
    disconnect,
    reconnect,
    send,
    messageCount
  };
} 