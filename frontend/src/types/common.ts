/**
 * 通用分页参数接口
 */
export interface PaginationParams {
  page?: number;
  size?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

/**
 * 分页响应结果接口
 */
export interface PaginatedResponse<T> {
  data: T[];
  meta: {
    pagination: {
      total: number;
      page: number;
      size: number;
      total_pages: number;
    };
  };
}

/**
 * 通用API响应接口
 */
export interface ApiResponse<T> {
  data: T;
  meta?: Record<string, any>;
}

/**
 * 通用错误响应接口
 */
export interface ErrorResponse {
  error: {
    code: string;
    message: string;
    details?: Record<string, any>;
  };
}

/**
 * 通用的键值对选项接口
 */
export interface SelectOption {
  label: string;
  value: string | number;
  disabled?: boolean;
}

/**
 * 排序方向
 */
export type SortOrder = 'asc' | 'desc' | false;

/**
 * 通用筛选条件接口
 */
export interface FilterCondition {
  field: string;
  operator: 'eq' | 'neq' | 'gt' | 'gte' | 'lt' | 'lte' | 'in' | 'nin' | 'like' | 'between';
  value: any;
}

/**
 * 时间范围
 */
export interface TimeRange {
  start: Date | string | null;
  end: Date | string | null;
} 