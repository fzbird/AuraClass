export interface Notification {
  id: number;
  title: string;
  content: string;
  isRead: boolean;
  createdAt: string;
  updatedAt: string;
  type?: string;
  senderId?: number;
  senderName?: string;
  recipientId?: number;
}

export interface NotificationsResponse {
  data: Notification[];
  total: number;
}

export interface CreateNotificationPayload {
  title: string;
  content: string;
  // 通知类型：system-系统通知，quant-量化通知，message-消息通知，role-角色通知
  notification_type: string;
  // 接收者类型：all-所有用户，class-指定班级，user-指定用户
  recipient_type?: 'all' | 'class' | 'user';
  // 接收者用户ID数组（当接收者为用户时使用）
  user_ids?: number[];
  // 接收者班级ID数组（当接收者为班级时使用）
  class_ids?: number[];
  // 以下是原有的，可能已不用
  recipientUserId?: number;
  recipientRoleId?: number;
  recipientClassId?: number;
  type?: string;
} 