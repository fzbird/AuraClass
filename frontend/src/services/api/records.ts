import http from '../http';
import type { PaginatedResponse, ApiResponse } from '@/types/common';
import type { QuantRecord, CreateQuantRecordPayload, UpdateQuantRecordPayload } from '@/types/record';

// 定义请求参数接口，包含排序字段
interface QuantRecordsParams {
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  [key: string]: any;
}

// 定义分页响应接口
interface PaginatedItems<T> {
  items: T[];
  total: number;
}

/**
 * 获取量化记录列表
 * @param params 查询参数，支持分页、排序和筛选
 */
export async function getQuantRecords(params: Record<string, any> = {}) {
  try {
    console.log('发送量化记录请求，参数:', params);
    const response = await http.get<any>('/quant-records', { params });
    
    // 添加详细调试输出
    console.log('量化记录响应数据:', response);
    console.log('量化记录响应类型:', typeof response);
    if (response && typeof response === 'object') {
      console.log('量化记录响应键:', Object.keys(response));
      
      // 检查是否包含排序信息
      if (params.sort_by) {
        console.log('请求包含排序参数:', params.sort_by, params.sort_order);
      }
    }
    
    // 更灵活地解析不同的响应格式，直接返回记录数组
    if (Array.isArray(response)) {
      // 直接是数组
      console.log(`返回数组格式，包含 ${response.length} 条记录`);
      return response;
    } else if (response.data && Array.isArray(response.data)) {
      // response.data 是数组
      console.log(`返回 response.data 数组格式，包含 ${response.data.length} 条记录`);
      return response.data;
    } else if (response.data?.data && Array.isArray(response.data.data)) {
      // 嵌套格式 (data.data)
      console.log(`返回 response.data.data 数组格式，包含 ${response.data.data.length} 条记录`);
      return response.data.data;
    } else if (response && typeof response === 'object' && 'items' in response && Array.isArray((response as any).items)) {
      // 分页格式 (items)
      const responseWithItems = response as any;
      console.log(`返回 response.items 数组格式，包含 ${responseWithItems.items.length} 条记录`);
      
      return {
        items: responseWithItems.items,
        total: responseWithItems.total || responseWithItems.items.length
      } as PaginatedItems<QuantRecord>;
    } else {
      console.error('未知的量化记录响应格式:', response);
      return [];
    }
  } catch (error) {
    console.error('获取量化记录失败:', error);
    return [];
  }
}

/**
 * 获取单个量化记录详情
 * @param id 记录ID
 */
export async function getQuantRecord(id: number) {
  return http.get<{ data: QuantRecord }>(`/quant-records/${id}`);
}

/**
 * 创建量化记录
 * @param data 记录数据
 */
export async function createQuantRecord(data: CreateQuantRecordPayload) {
  return http.post<{ data: QuantRecord }>('/quant-records', data);
}

/**
 * 批量创建量化记录
 * @param records 记录数据数组
 */
export async function createQuantRecords(records: CreateQuantRecordPayload[]) {
  return http.post<{ 
    data: { 
      success: number; 
      failed?: Array<{
        data: Partial<CreateQuantRecordPayload>;
        reason: string;
      }>;
    } 
  }>('/quant-records/batch', { records });
}

/**
 * 更新量化记录
 * @param id 记录ID
 * @param data 更新的记录数据
 */
export async function updateQuantRecord(id: number, data: UpdateQuantRecordPayload) {
  return http.put<{ data: QuantRecord }>(`/quant-records/${id}`, data);
}

/**
 * 删除量化记录
 * @param id 记录ID
 */
export async function deleteQuantRecord(id: number) {
  return http.delete(`/quant-records/${id}`);
}

/**
 * 导出量化记录
 * @param params 查询参数
 */
export async function exportQuantRecords(params = {}) {
  return http.get('/quant-records/export', { 
    params,
    responseType: 'blob'
  }).then(response => {
    // 确保response是Blob对象
    if (response instanceof Blob) {
      return response;
    } else if (response.data instanceof Blob) {
      return response.data;
    } else {
      throw new Error('导出响应格式错误：预期为Blob');
    }
  });
}

/**
 * 获取量化记录统计信息
 * @param params 查询参数
 */
export async function getQuantRecordsStatistics(params = {}) {
  return http.get<{
    data: {
      total_records: number;
      total_score: number;
      average_score: number;
      positive_records: number;
      negative_records: number;
      by_date: Array<{
        date: string;
        count: number;
        score_sum: number;
      }>;
      by_item: Array<{
        item_id: number;
        item_name: string;
        count: number;
        score_sum: number;
      }>;
    }
  }>('/quant-records/statistics', { params });
}

/**
 * 导入量化记录
 * @param formData 包含CSV文件的FormData
 */
export async function importQuantRecords(formData: FormData) {
  return http.post<{
    data: {
      success: number;
      failed?: Array<{
        row: number;
        reason: string;
      }>;
    }
  }>('/quant-records/import', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
}

/**
 * 批量创建量化记录（增强版，支持学号）
 * @param records 记录数据数组，支持通过学号关联学生
 */
export async function importRecords(records: Array<{
  student_id?: number;
  student_id_no?: string;
  item_id: number;
  score: number;
  reason?: string;
  record_date?: string;
}>) {
  return http.post<{ 
    data: { 
      success: number; 
      failed?: Array<{
        data: {
          student_id?: number;
          student_id_no?: string;
          item_id: number;
          score: number;
          reason?: string;
          record_date?: string;
        };
        reason: string;
      }>;
    } 
  }>('/quant-records/batch', { records });
}

/**
 * 获取量化记录列表
 * @param params 查询参数
 */
export async function getRecords(params = {}) {
  try {
    const response = await http.get<any>('/quant-records', { params });
    console.log('获取量化记录原始响应:', response);
    
    // 处理可能的不同响应格式
    if (response && response.data && Array.isArray(response.data)) {
      // 标准格式: { data: QuantRecord[] }
      return { data: response.data };
    } else if (Array.isArray(response)) {
      // 直接返回了数组格式
      return { data: response };
    } else if (response && typeof response === 'object' && 'items' in response && Array.isArray(response.items)) {
      // 分页格式: { items: QuantRecord[], total: number }
      return { 
        data: response.items, 
        meta: { 
          pagination: { 
            total: response.total || response.items.length 
          } 
        } 
      };
    } else {
      console.error('未知的量化记录响应格式:', response);
      return { data: [] };
    }
  } catch (error) {
    console.error('获取量化记录失败:', error);
    return { data: [] };
  }
} 