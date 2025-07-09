import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { 
  getNotifications, 
  markNotificationAsRead, 
  deleteNotification,
  createNotification
} from '@/services/api/notifications';
import type { Notification, CreateNotificationPayload } from '@/types/notification';
import { 
  extractNotificationsFromResponse, 
  normalizeNotification, 
  formatApiError 
} from '@/utils/notification-helpers';

export const useNotificationStore = defineStore('notification', () => {
  // 状态
  const notifications = ref<Notification[]>([]);
  const total = ref(0);
  const loading = ref(false);
  const currentPage = ref(1);
  const pageSize = ref(10);
  
  // 计算属性
  const unreadCount = computed(() => 
    notifications.value.filter(notification => !notification.isRead).length
  );
  
  const recentNotifications = computed(() => 
    notifications.value.slice(0, 5)
  );
  
  // 获取通知列表
  async function fetchNotifications(params = {}) {
    loading.value = true;
    
    try {
      const defaultParams = {
        page: currentPage.value,
        pageSize: pageSize.value
      };
      
      const mergedParams = { ...defaultParams, ...params };
      
      const response = await getNotifications(mergedParams);
      const { notifications: fetchedNotifications, total: totalCount } = 
        extractNotificationsFromResponse(response);
      
      notifications.value = fetchedNotifications;
      total.value = totalCount;
    } catch (error) {
      console.error('获取通知列表失败:', formatApiError(error));
    } finally {
      loading.value = false;
    }
  }
  
  // 标记通知为已读
  async function markAsRead(id: number) {
    try {
      const response = await markNotificationAsRead(id);
      
      // 更新本地数据
      const index = notifications.value.findIndex(notification => notification.id === id);
      if (index !== -1) {
        notifications.value[index].isRead = true;
      }
      
      return { success: true };
    } catch (error) {
      console.error('标记通知为已读失败:', formatApiError(error));
      return { 
        success: false, 
        error: formatApiError(error) 
      };
    }
  }
  
  // 删除通知
  async function remove(id: number) {
    try {
      await deleteNotification(id);
      
      // 删除成功 - 从列表中移除
      notifications.value = notifications.value.filter(notification => notification.id !== id);
      total.value--;
      
      return { success: true, message: '通知已成功删除' };
    } catch (error: any) {
      console.error('删除通知失败:', formatApiError(error));
      
      // 处理特定类型的错误
      const statusCode = error.response?.status;
      const errorDetail = error.response?.data?.detail || '';
      
      // 根据具体错误消息提供更细化的反馈
      if (statusCode === 403) {
        if (errorDetail.includes('已读通知')) {
          return {
            success: false,
            error: '已读通知不可删除',
            message: '发送者不能删除已被阅读的通知',
            code: 403,
            subtype: 'read_notification'
          };
        } else {
          return {
            success: false,
            error: '权限不足',
            message: '您没有权限删除这条通知',
            code: 403,
            subtype: 'permission_denied'
          };
        }
      } else if (statusCode === 404) {
        return {
          success: false,
          error: '通知不存在',
          message: '要删除的通知不存在或已被删除',
          code: 404
        };
      }
      
      // 其他错误情况
      return { 
        success: false, 
        error: formatApiError(error),
        message: `删除通知失败: ${formatApiError(error)}`,
        code: statusCode || 500
      };
    }
  }
  
  // 创建通知
  async function create(data: CreateNotificationPayload) {
    try {
      const response = await createNotification(data);
      
      // 提取并规范化新通知数据
      const newNotification = normalizeNotification(response.data);
      
      // 如果是第一页，添加到列表顶部
      if (newNotification && currentPage.value === 1) {
        notifications.value = [newNotification, ...notifications.value];
        total.value++;
      }
      
      return { success: true, notification: newNotification };
    } catch (error) {
      console.error('创建通知失败:', formatApiError(error));
      return { 
        success: false, 
        error: formatApiError(error) 
      };
    }
  }
  
  // 设置分页
  function setPagination(page: number, size: number = pageSize.value) {
    currentPage.value = page;
    pageSize.value = size;
  }
  
  return {
    notifications,
    total,
    loading,
    currentPage,
    pageSize,
    unreadCount,
    recentNotifications,
    fetchNotifications,
    markAsRead,
    remove,
    create,
    setPagination
  };
});
