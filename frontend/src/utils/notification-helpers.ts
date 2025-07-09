import type { Notification } from '@/types/notification';

/**
 * 标准化通知数据，处理后端返回的不同字段名称
 * @param data 后端返回的通知数据
 * @returns 标准化后的通知对象
 */
export function normalizeNotification(data: any): Notification | null {
  if (!data) return null;
  
  // 构建标准化的通知对象
  return {
    id: data.id,
    title: data.title,
    content: data.content,
    // 处理不同的已读状态字段
    isRead: data.is_read ?? data.isRead ?? false,
    // 处理不同的时间字段
    createdAt: data.created_at ?? data.createdAt ?? new Date().toISOString(),
    updatedAt: data.updated_at ?? data.updatedAt ?? new Date().toISOString(),
    // 处理类型字段
    type: data.notification_type ?? data.type,
    // 处理发送者信息
    senderId: data.sender_id ?? data.senderId,
    senderName: data.sender_name ?? data.senderName,
    // 处理接收者信息
    recipientId: data.recipient_user_id ?? data.recipientId,
  };
}

/**
 * 标准化通知列表数据
 * @param dataArray 后端返回的通知数据数组
 * @returns 标准化后的通知对象数组
 */
export function normalizeNotifications(dataArray: any[]): Notification[] {
  if (!Array.isArray(dataArray)) return [];
  return dataArray.map(item => normalizeNotification(item)).filter(Boolean) as Notification[];
}

/**
 * 从API响应中提取标准化的通知列表
 * @param response API响应对象
 * @returns 提取的通知列表和总数
 */
export function extractNotificationsFromResponse(response: any): { 
  notifications: Notification[],
  total: number
} {
  if (!response) {
    return { notifications: [], total: 0 };
  }
  
  let result: Notification[] = [];
  let total = 0;
  
  // 处理响应数据
  const data = response.data;
  
  if (data) {
    // 处理标准格式响应: { data: [...], meta: { count: X } }
    if (data.data && Array.isArray(data.data)) {
      result = normalizeNotifications(data.data);
      total = data.meta?.count || data.total || result.length;
    } 
    // 处理直接数组格式响应: [...]
    else if (Array.isArray(data)) {
      result = normalizeNotifications(data);
      total = result.length;
    }
  }
  
  return { notifications: result, total };
}

/**
 * 生成标准错误消息
 * @param error 错误对象
 * @returns 格式化的错误消息
 */
export function formatApiError(error: any): string {
  if (!error) return '未知错误';
  
  // 尝试从API响应中提取详细错误信息
  const statusCode = error.response?.status;
  const apiErrorDetail = error.response?.data?.detail;
  const errorMessage = error.message;
  
  // 构建详细错误消息
  if (statusCode && apiErrorDetail) {
    return `错误(${statusCode}): ${apiErrorDetail}`;
  } else if (apiErrorDetail) {
    return apiErrorDetail;
  } else if (errorMessage) {
    return errorMessage;
  }
  
  return '未知错误';
} 