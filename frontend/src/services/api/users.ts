import http from '../http';
import type { User } from '@/types/user';

/**
 * 获取用户列表
 * @param params 查询参数
 * @returns 用户列表
 */
export async function getUsers(params = {}) {
  try {
    const response = await http.get<{ data: User[] }>('/users', { params });
    console.log('用户列表响应:', response);
    
    // 处理不同的响应格式
    if (response?.data?.data && Array.isArray(response.data.data)) {
      // 标准的分页响应格式：{ data: { data: [...], meta: {...} } }
      return { data: response.data.data };
    } else if (response?.data && Array.isArray(response.data)) {
      // 直接数组响应：{ data: [...] }
      return { data: response.data };
    } else if (Array.isArray(response)) {
      // 直接是数组
      return { data: response };
    } else {
      console.error('未识别的用户数据响应格式:', response);
      return { data: [] };
    }
  } catch (error) {
    console.error('获取用户列表失败:', error);
    return { data: [] };
  }
}

/**
 * 获取单个用户信息
 * @param id 用户ID
 * @returns 用户信息
 */
export async function getUser(id: number) {
  try {
    const response = await http.get<{ data: User }>(`/users/${id}`);
    return response;
  } catch (error) {
    console.error(`获取用户信息(ID:${id})失败:`, error);
    throw error;
  }
}

/**
 * 创建用户
 * @param data 用户数据
 * @returns 创建的用户信息
 */
export async function createUser(data: any) {
  return http.post<{ data: User }>('/users', data);
}

/**
 * 更新用户
 * @param id 用户ID
 * @param data 更新数据
 * @returns 更新后的用户信息
 */
export async function updateUser(id: number, data: any) {
  return http.put<{ data: User }>(`/users/${id}`, data);
}

/**
 * 删除用户
 * @param id 用户ID
 * @returns 操作结果
 */
export async function deleteUser(id: number) {
  return http.delete(`/users/${id}`);
}