import http from '../http';
import type { Notification, NotificationsResponse, CreateNotificationPayload } from '@/types/notification';

/**
 * 获取通知列表
 */
export async function getNotifications(params = {}) {
  const response = await http.get<NotificationsResponse>('/notifications', { params });
  return response;
}

/**
 * 获取单个通知详情
 */
export async function getNotification(id: number) {
  const response = await http.get<{ data: Notification }>(`/notifications/${id}`);
  return response;
}

/**
 * 创建通知
 */
export async function createNotification(data: CreateNotificationPayload) {
  console.log('创建通知请求数据:', data);
  try {
    const response = await http.post<Notification>('/notifications', data);
    console.log('创建通知响应:', response);
    return response;
  } catch (error) {
    console.error('创建通知失败:', error);
    // 重新抛出错误以便调用者处理
    throw error;
  }
}

/**
 * 标记通知为已读
 */
export async function markNotificationAsRead(id: number) {
  const response = await http.patch<Notification>(`/notifications/${id}/read`);
  return response;
}

/**
 * 标记所有通知为已读
 */
export async function markAllNotificationsAsRead() {
  return http.patch<void>('/notifications/read-all');
}

/**
 * 删除通知
 * @param id 通知ID
 * @returns 删除的通知数据
 */
export async function deleteNotification(id: number) {
  console.log('删除通知，ID:', id);
  try {
    // 使用DELETE方法 - 匹配后端API实现
    const response = await http.delete(`/notifications/${id}`);
    console.log('通知删除成功，响应:', response);
    return response;
  } catch (error: any) {
    // 提取错误信息以便调试
    const statusCode = error.response?.status;
    const errorDetail = error.response?.data?.detail || error.message;
    console.error(`删除通知失败: 状态码=${statusCode}, 错误=${errorDetail}`);
    
    // 重新抛出错误，保留原始错误信息
    throw error;
  }
}

/**
 * 获取未读通知数量
 */
export async function getUnreadNotificationsCount() {
  try {
    const response = await http.get<{ data: { count: number } }>('/notifications/unread-count');
    // 根据API响应结构正确访问数据
    if (response && response.data && response.data.data) {
      return response.data.data.count;
    } else if (response && typeof response.data === 'object' && 'count' in response.data) {
      // 处理可能的替代响应格式
      return response.data.count;
    }
    // 默认返回0
    return 0;
  } catch (error) {
    console.error('获取未读通知数量失败:', error);
    return 0;
  }
}

/**
 * 标记通知为已读（别名函数，兼容现有代码）
 */
export async function markAsRead(id: number) {
  return markNotificationAsRead(id);
}
