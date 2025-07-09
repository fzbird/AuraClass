import { ref, onMounted, onUnmounted, watch } from 'vue';
import { useUserStore } from '@/stores/user';
import { useWebSocketStore } from '@/stores/websocket';
import { useBaseWebSocket } from '@/services/websocket/base';
import { useMessage } from 'naive-ui';

export function useRealtimeUpdates() {
  const userStore = useUserStore();
  const wsStore = useWebSocketStore();
  const message = useMessage();
  
  // 创建WebSocket连接
  const { 
    isConnected, 
    socket, 
    connect, 
    disconnect, 
    isConnecting, 
    connectionError 
  } = useBaseWebSocket('/ws/notifications');
  
  // 新通知和数据更新标志
  const hasNewNotifications = ref(false);
  const hasDashboardUpdate = ref(false);
  const hasStudentsUpdate = ref(false);
  const hasRecordsUpdate = ref(false);
  const hasItemsUpdate = ref(false);
  
  // 监听WebSocket连接状态
  watch(isConnected, (connected) => {
    if (connected) {
      message.success('实时更新已连接');
    } else if (connectionError.value) {
      // 显示连接错误信息
      message.error(`实时更新连接失败: ${connectionError.value}`);
      console.error('WebSocket连接失败:', connectionError.value);
    }
  });
  
  // 处理WebSocket消息
  const handleWebSocketMessage = (event: MessageEvent) => {
    try {
      const data = JSON.parse(event.data);
      console.log('WebSocket收到消息:', data);
      
      // 根据消息类型处理不同的更新
      if (data.type === 'notification') {
        // 新通知
        hasNewNotifications.value = true;
        message.info('收到新通知');
      } else if (data.type === 'update') {
        // 数据更新
        const updateType = data.data?.update_type;
        
        switch(updateType) {
          case 'dashboard':
            hasDashboardUpdate.value = true;
            message.info('仪表盘数据已更新');
            break;
          case 'students':
            hasStudentsUpdate.value = true;
            message.info('学生数据已更新');
            break;
          case 'records':
            hasRecordsUpdate.value = true;
            message.info('量化记录已更新');
            break;
          case 'items':
            hasItemsUpdate.value = true;
            message.info('量化项目已更新');
            break;
          default:
            // 未知更新类型
            break;
        }
      }
    } catch (error) {
      console.error('WebSocket消息处理出错:', error);
    }
  };
  
  // 初始化WebSocket消息处理
  const initMessageHandler = () => {
    if (socket.value) {
      socket.value.onmessage = handleWebSocketMessage;
    }
  };
  
  // 重置更新标志
  const resetUpdateFlags = () => {
    hasNewNotifications.value = false;
    hasDashboardUpdate.value = false;
    hasStudentsUpdate.value = false;
    hasRecordsUpdate.value = false;
    hasItemsUpdate.value = false;
  };
  
  // 启用实时更新
  const enableRealtimeUpdates = () => {
    wsStore.updateConfig({ enabled: true });
    if (!isConnected.value && !isConnecting.value) {
      connect();
      initMessageHandler();
    }
  };
  
  // 禁用实时更新
  const disableRealtimeUpdates = () => {
    disconnect();
    wsStore.updateConfig({ enabled: false });
  };
  
  onMounted(() => {
    // 检查WebSocket配置
    if (wsStore.config.enabled && userStore.isLoggedIn) {
      console.log('初始化WebSocket连接');
      connect();
      // 设置消息处理器
      initMessageHandler();
    }
  });
  
  onUnmounted(() => {
    disconnect();
  });
  
  // 重新连接
  const reconnect = () => {
    console.log('尝试重新连接WebSocket');
    disconnect();
    connect();
    initMessageHandler();
  };
  
  return {
    isConnected,
    isConnecting,
    connectionError,
    hasNewNotifications,
    hasDashboardUpdate,
    hasStudentsUpdate,
    hasRecordsUpdate,
    hasItemsUpdate,
    enableRealtimeUpdates,
    disableRealtimeUpdates,
    resetUpdateFlags,
    reconnect
  };
} 