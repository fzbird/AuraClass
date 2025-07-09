import { ref, watch, computed, onMounted } from 'vue';
import { useUserStore } from '@/stores/user';
import { useNotificationStore } from '@/stores/notification';
import { useBaseWebSocket } from './base';
import type { Notification } from '@/types/notification';
import { NotificationService, requestNotificationPermission, getNotificationPermission, isNotificationSupported } from '@/utils/notification';
import wsConfig from './config';

// 确保与浏览器内置的Notification类型区分开
type BrowserNotification = Notification;

/**
 * 通知WebSocket服务
 * 提供实时通知接收、通知确认等功能
 */
export function useNotificationWebSocket() {
  const notificationStore = useNotificationStore();
  const userStore = useUserStore();
  
  // 检查WebSocket功能是否启用
  const isWebSocketEnabled = computed(() => wsConfig.enabled);
  
  // 创建基础WebSocket连接
  const {
    socket,
    isConnected,
    isConnecting,
    connectionError,
    connect,
    disconnect,
    reconnect,
    send
  } = useBaseWebSocket('/ws/notifications', {
    debug: import.meta.env.DEV, // 开发环境开启调试
    heartbeatInterval: 45000    // 45秒心跳
  });
  
  // 初始化通知服务
  const notificationService = NotificationService.getInstance();
  
  // 最近接收的通知
  const latestNotification = ref<Notification | null>(null);
  // 是否支持浏览器通知
  const browserNotificationsSupported = isNotificationSupported();
  // 浏览器通知权限状态
  const browserNotificationsPermission = ref(
    browserNotificationsSupported ? getNotificationPermission() : 'denied'
  );
  
  // 当收到新通知时的处理函数
  const handleNotificationReceived = (data: any) => {
    if (!data) {
      console.error('收到空的WebSocket消息');
      return;
    }
    
    // 检查消息类型
    if (data.type === 'notification' && data.data) {
      try {
        // 保存最新通知
        const newNotification: Notification = {
          id: data.data.id,
          title: data.data.title || '新通知',
          content: data.data.content || '',
          createdAt: data.data.created_at || new Date().toISOString(),
          updatedAt: data.data.updated_at || data.data.created_at || new Date().toISOString(),
          isRead: false,
          type: data.data.notification_type || 'system',
          senderId: data.data.sender_id,
        };
        
        // 打印调试信息
        if (import.meta.env.DEV) {
          console.log('收到新通知:', newNotification);
        }
        
        latestNotification.value = newNotification;
        
        // 更新通知商店
        notificationStore.fetchNotifications(); // 重新获取通知列表
        
        // 显示浏览器通知
        showBrowserNotification(newNotification);
      } catch (error) {
        console.error('处理通知数据失败:', error, data);
      }
    } else if (data.type === 'pong') {
      // 心跳响应，忽略
      return;
    } else {
      console.warn('收到未知类型的WebSocket消息:', data);
    }
  };
  
  // 请求浏览器通知权限
  const requestBrowserNotificationPermission = async (): Promise<boolean> => {
    const granted = await requestNotificationPermission();
    browserNotificationsPermission.value = getNotificationPermission();
    return granted;
  };
  
  // 显示浏览器通知
  const showBrowserNotification = (notification: Notification) => {
    if (!browserNotificationsSupported || browserNotificationsPermission.value !== 'granted') {
      return null;
    }
    
    return notificationService.show({
      title: notification.title,
      body: notification.content,
      icon: '/favicon.ico',
      tag: `notification-${notification.id}`,
      requireInteraction: false,
      silent: false,
      onClick: () => {
        // 标记为已读
        notificationStore.markAsRead(notification.id);
        
        // 聚焦窗口
        window.focus();
        
        // 可选：打开相关页面
        // router.push({ name: 'Notifications' });
      }
    });
  };
  
  // 发送通知确认
  const sendAcknowledge = (notificationId: number) => {
    if (isConnected.value) {
      return send({
        type: 'ack',
        notification_id: notificationId
      });
    }
    return false;
  };
  
  // 安全解析JSON
  const safeParseJSON = (text: string) => {
    try {
      return JSON.parse(text);
    } catch (error) {
      console.error('JSON解析失败:', error, text);
      return null;
    }
  };
  
  // 监听WebSocket消息
  const setupMessageListener = (ws: WebSocket) => {
    if (!ws) return;
    
    ws.onmessage = (event) => {
      try {
        // 检查数据是否为空
        if (!event.data) {
          console.warn('收到空消息');
          return;
        }
        
        // 解析JSON数据
        const data = typeof event.data === 'string' 
          ? safeParseJSON(event.data) 
          : event.data;
          
        if (data) {
          handleNotificationReceived(data);
        }
      } catch (error) {
        console.error('处理WebSocket消息出错:', error);
      }
    };
  };
  
  // 监听WebSocket变化
  watch(socket, (newSocket) => {
    if (newSocket) {
      setupMessageListener(newSocket);
    }
  });
  
  // 初始化连接
  const initializeConnection = () => {
    // 如果用户已登录且WebSocket功能已启用，则连接
    if (userStore.isLoggedIn && isWebSocketEnabled.value && !isConnected.value && !isConnecting.value) {
      connect();
      
      // 是否支持浏览器通知
      if (browserNotificationsSupported && browserNotificationsPermission.value === 'default') {
        // 当WebSocket连接成功后，请求通知权限
        requestBrowserNotificationPermission();
      }
    }
  };
  
  // 在组件挂载时执行初始化
  onMounted(() => {
    initializeConnection();
    
    // 组件创建后，自动请求通知权限
    if (browserNotificationsSupported && browserNotificationsPermission.value === 'default') {
      requestBrowserNotificationPermission();
    }
  });
  
  return {
    socket,
    isConnected,
    isConnecting,
    connectionError,
    latestNotification,
    connect,
    disconnect,
    reconnect,
    sendAcknowledge,
    showBrowserNotification,
    requestBrowserNotificationPermission,
    browserNotificationsSupported,
    browserNotificationsPermission,
    isWebSocketEnabled,
    initializeConnection
  };
} 