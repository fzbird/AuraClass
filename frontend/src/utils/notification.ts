/**
 * 浏览器通知工具
 * 提供统一的浏览器通知管理接口
 */

// 检查浏览器通知支持
export const isNotificationSupported = (): boolean => {
  return 'Notification' in window;
};

// 获取当前通知权限
export const getNotificationPermission = (): NotificationPermission => {
  if (!isNotificationSupported()) {
    return 'denied';
  }
  return Notification.permission;
};

// 请求通知权限
export const requestNotificationPermission = async (): Promise<boolean> => {
  if (!isNotificationSupported()) {
    return false;
  }
  
  try {
    const permission = await Notification.requestPermission();
    return permission === 'granted';
  } catch (error) {
    console.error('请求通知权限失败:', error);
    return false;
  }
};

// 自定义通知选项接口（扩展浏览器原生NotificationOptions）
export interface CustomNotificationOptions {
  title: string;
  body?: string;
  icon?: string;
  tag?: string;
  data?: any;
  requireInteraction?: boolean;
  silent?: boolean;
  onClick?: () => void;
  onClose?: () => void;
  onError?: (error: Event) => void;
  onShow?: () => void;
}

// 显示通知
export const showNotification = (options: CustomNotificationOptions): Notification | null => {
  if (!isNotificationSupported() || Notification.permission !== 'granted') {
    return null;
  }
  
  try {
    // 提取浏览器原生NotificationOptions支持的属性
    const notification = new Notification(options.title, {
      body: options.body,
      icon: options.icon || '/favicon.ico',
      tag: options.tag,
      data: options.data,
      requireInteraction: options.requireInteraction,
      silent: options.silent
    });
    
    // 添加事件监听器
    if (options.onClick) {
      notification.onclick = options.onClick;
    }
    
    if (options.onClose) {
      notification.onclose = options.onClose;
    }
    
    if (options.onError) {
      notification.onerror = options.onError;
    }
    
    if (options.onShow) {
      notification.onshow = options.onShow;
    }
    
    return notification;
  } catch (error) {
    console.error('显示通知失败:', error);
    return null;
  }
};

// 关闭通知
export const closeNotification = (notification: Notification): void => {
  if (notification) {
    notification.close();
  }
};

// 检查是否支持通知权限查询
export const canQueryPermission = (): boolean => {
  return isNotificationSupported() && typeof Notification.permission === 'string';
};

/**
 * 通知服务类
 * 提供统一的通知管理接口
 */
export class NotificationService {
  private static instance: NotificationService;
  private activeNotifications: Map<string, Notification> = new Map();
  
  private constructor() {
    // 私有构造函数，确保单例
  }
  
  // 获取实例
  public static getInstance(): NotificationService {
    if (!NotificationService.instance) {
      NotificationService.instance = new NotificationService();
    }
    return NotificationService.instance;
  }
  
  // 显示通知
  public show(options: CustomNotificationOptions): string | null {
    const notificationId = options.tag || `notification-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
    
    // 如果已存在相同tag的通知，先关闭
    if (options.tag && this.activeNotifications.has(options.tag)) {
      this.close(options.tag);
    }
    
    const notification = showNotification({
      ...options,
      tag: notificationId,
      onClick: () => {
        if (options.onClick) {
          options.onClick();
        }
        // 从活动通知中移除
        this.activeNotifications.delete(notificationId);
      },
      onClose: () => {
        if (options.onClose) {
          options.onClose();
        }
        // 从活动通知中移除
        this.activeNotifications.delete(notificationId);
      },
      onError: (error) => {
        if (options.onError) {
          options.onError(error);
        }
        // 从活动通知中移除
        this.activeNotifications.delete(notificationId);
      }
    });
    
    if (notification) {
      this.activeNotifications.set(notificationId, notification);
      return notificationId;
    }
    
    return null;
  }
  
  // 关闭通知
  public close(notificationId: string): boolean {
    const notification = this.activeNotifications.get(notificationId);
    if (notification) {
      notification.close();
      this.activeNotifications.delete(notificationId);
      return true;
    }
    return false;
  }
  
  // 关闭所有通知
  public closeAll(): void {
    this.activeNotifications.forEach((notification) => {
      notification.close();
    });
    this.activeNotifications.clear();
  }
  
  // 获取活动通知数量
  public getActiveCount(): number {
    return this.activeNotifications.size;
  }
  
  // 获取通知列表
  public getActiveNotifications(): string[] {
    return Array.from(this.activeNotifications.keys());
  }
} 