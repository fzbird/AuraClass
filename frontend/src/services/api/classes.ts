import http from '../http';
import type { PaginatedResponse } from '@/types/common';
import type { Class, CreateClassPayload, UpdateClassPayload } from '@/types/class';

/**
 * 获取班级列表
 * @param params 查询参数
 */
export async function getClasses(params = {}) {
  try {
    const response = await http.get<PaginatedResponse<Class>>('/classes', { params });
    
    // 添加调试输出
    console.log('班级数据响应:', response);
    console.log('班级数据响应类型:', typeof response);
    console.log('班级数据响应键:', Object.keys(response));
    
    // 更灵活地解析不同的响应格式
    if (Array.isArray(response)) {
      // 直接是数组
      return { data: { data: response } };
    } else if (response.data && Array.isArray(response.data)) {
      // response.data 是数组
      return { data: { data: response.data } };
    } else if (response.data?.data && Array.isArray(response.data.data)) {
      // 标准格式
      return response;
    } else {
      console.error('未知的班级数据响应格式:', response);
      return { data: { data: [] } };
    }
  } catch (error) {
    console.error('获取班级数据失败:', error);
    return { data: { data: [] } };
  }
}

/**
 * 获取单个班级详情
 * @param id 班级ID
 */
export async function getClass(id: number) {
  return http.get<{ data: Class }>(`/classes/${id}`);
}

/**
 * 创建班级
 * @param data 班级数据
 */
export async function createClass(data: CreateClassPayload) {
  return http.post<{ data: Class }>('/classes', data);
}

/**
 * 更新班级信息
 * @param id 班级ID
 * @param data 更新的班级数据
 */
export async function updateClass(id: number, data: UpdateClassPayload) {
  return http.put<{ data: Class }>(`/classes/${id}`, data);
}

/**
 * 删除班级
 * @param id 班级ID
 */
export async function deleteClass(id: number) {
  return http.delete(`/classes/${id}`);
}

/**
 * 获取班级的学生
 * @param id 班级ID
 * @param params 查询参数
 */
export async function getClassStudents(id: number, params = {}) {
  return http.get<PaginatedResponse<any>>(`/classes/${id}/students`, { params });
}

/**
 * 获取班级的量化记录统计
 * @param id 班级ID
 * @param params 查询参数
 */
export async function getClassStatistics(id: number, params = {}) {
  return http.get<{ data: any }>(`/classes/${id}/statistics`, { params });
} 