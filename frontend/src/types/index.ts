// 通用响应类型
export interface ApiResponse<T> {
  data: T;
  meta?: {
    pagination?: {
      page: number;
      size: number;
      total: number;
    };
  };
}

// 通用错误响应
export interface ApiError {
  error: {
    code: string;
    message: string;
    details?: any;
  };
}

// 用户类型
export interface User {
  id: number;
  username: string;
  full_name: string;
  role_id: number;
  class_id?: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// 登录请求
export interface LoginRequest {
  username: string;
  password: string;
}

// 登录响应
export interface LoginResponse {
  access_token: string;
  token_type: string;
}

// 学生类型
export interface Student {
  id: number;
  user_id?: number;
  student_id_no: string;
  full_name: string;
  class_id: number;
  gender: string;
  birth_date?: string;
  contact_info?: string;
  created_at: string;
  updated_at: string;
}

// 量化项目
export interface QuantItem {
  id: number;
  name: string;
  description?: string;
  default_score: number;
  category: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// 量化记录
export interface QuantRecord {
  id: number;
  student_id: number;
  item_id: number;
  score: number;
  reason?: string;
  recorder_id: number;
  record_date: string;
  created_at: string;
  updated_at: string;
  student?: Student;
  item?: QuantItem;
}

// 通知
export interface Notification {
  id: number;
  title: string;
  content: string;
  recipient_user_id?: number;
  recipient_role_id?: number;
  recipient_class_id?: number;
  sender_id: number;
  created_at: string;
  is_read: boolean;
}

// 班级
export interface Class {
  id: number;
  name: string;
  grade: string;
  year: number;
  head_teacher_id?: number;
  created_at: string;
  updated_at: string;
}

// 角色
export interface Role {
  id: number;
  name: string;
  description?: string;
  created_at: string;
}

// 统计数据接口
export interface StatisticsSummary {
  total_students: number;
  total_records: number;
  average_score: number;
  categories: {
    category: string;
    count: number;
    average: number;
  }[];
}

// 导出所有类型定义
// 使用命名空间重导出，避免命名冲突
import * as notificationTypes from './notification';
import * as studentTypes from './student';
import * as statisticsTypes from './statistics';
import * as quantItemTypes from './quant-item';
import * as assistantTypes from './assistant';

export { 
  notificationTypes,
  studentTypes,
  statisticsTypes,
  quantItemTypes,
  assistantTypes
};
