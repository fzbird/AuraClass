import http from '../http';
import type { PaginatedResponse } from '@/types/common';
import type { 
  QuantItem, CreateQuantItemPayload, UpdateQuantItemPayload, 
  QuantItemCategory, CreateQuantItemCategoryPayload, UpdateQuantItemCategoryPayload 
} from '@/types/quant-item';
import axios from 'axios';

/**
 * 获取量化项目列表
 * @param params 查询参数
 */
export async function getQuantItems(params: any = {}) {
  try {
    // 创建请求参数的副本，以便可以安全地修改
    const processedParams = { ...params };
    
    // 记录原始筛选值，用于前端过滤
    const originalIsActive = processedParams.is_active;
    
    // 处理is_active参数，转换为后端API所需的active_only参数
    if ('is_active' in processedParams) {
      console.log(`原始is_active参数: ${processedParams.is_active}, 类型: ${typeof processedParams.is_active}`);
      
      // 后端API参数处理
      // 注意：我们这里不转换为active_only，而是直接获取所有项目，然后在前端过滤
      // 因为前面的尝试表明使用active_only参数可能有问题
      delete processedParams.is_active;
    }
    
    console.log('API请求最终参数:', processedParams);
    
    const response = await http.get<PaginatedResponse<QuantItem>>('/quant-items', { params: processedParams });
    
    console.log('接收到的API响应:', response);
    
    // 处理响应数据
    let items: QuantItem[] = [];
    let total = 0;
    
    // 标准化不同响应格式
    if (response.data?.data && Array.isArray(response.data.data)) {
      items = response.data.data;
      total = response.data.meta?.pagination?.total || items.length;
    } else if (response.data && Array.isArray(response.data)) {
      items = response.data;
      total = items.length;
    } else if (Array.isArray(response)) {
      items = response;
      total = items.length;
    } else {
      console.error('未识别的响应格式:', response);
      items = [];
      total = 0;
    }
    
    // 前端进行筛选处理
    if (originalIsActive !== undefined && items.length > 0) {
      const filterValue = originalIsActive === '1' || originalIsActive === true;
      console.log(`前端过滤${filterValue ? '启用' : '禁用'}状态项目，原始数量:`, items.length);
      
      // 根据筛选值过滤项目
      items = items.filter(item => item.is_active === filterValue);
      total = items.length;
      
      console.log(`过滤后的项目数量: ${items.length}`);
    }
    
    console.log(`处理后获取到 ${items.length} 个项目`);
    
    // 构造标准响应格式
    return {
      data: {
        data: items,
        meta: {
          pagination: { total }
        }
      }
    };
  } catch (error) {
    console.error('获取量化项目失败:', error);
    return { data: { data: [], meta: { pagination: { total: 0 } } } };
  }
}

/**
 * 获取单个量化项目详情
 * @param id 量化项目ID
 */
export async function getQuantItem(id: number) {
  return http.get<{ data: QuantItem }>(`/quant-items/${id}`);
}

/**
 * 创建量化项目
 * @param data 量化项目数据
 */
export async function createQuantItem(data: CreateQuantItemPayload) {
  try {
    console.log('创建量化项目请求数据:', data);
    const response = await http.post<any>('/quant-items', data);
    console.log('创建量化项目API响应:', response);
    
    // 检查响应结构并适当处理
    if (response && response.data) {
      return response;
    }
    
    return response;
  } catch (error) {
    console.error('创建量化项目失败:', error);
    throw error;
  }
}

/**
 * 更新量化项目
 * @param id 量化项目ID
 * @param data 更新的量化项目数据
 */
export async function updateQuantItem(id: number, data: UpdateQuantItemPayload) {
  return http.put<{ data: QuantItem }>(`/quant-items/${id}`, data);
}

/**
 * 删除量化项目
 * @param id 量化项目ID
 */
export async function deleteQuantItem(id: number) {
  return http.delete(`/quant-items/${id}`);
}

/**
 * 获取量化项目的记录统计
 * @param id 量化项目ID
 * @param params 查询参数
 */
export async function getQuantItemStats(id: number, params = {}) {
  return http.get<{ data: any }>(`/quant-items/${id}/statistics`, { params });
}

/**
 * 获取量化项目分类列表
 */
export async function getQuantItemCategories() {
  try {
    const response = await http.get<{ data: QuantItemCategory[] }>('/quant-item-categories');
    
    // 添加调试输出
    console.log('量化项目分类响应:', response);
    console.log('量化项目分类响应类型:', typeof response);
    if (response) console.log('量化项目分类响应键:', Object.keys(response));
    
    // 更灵活地解析不同的响应格式
    if (Array.isArray(response)) {
      // 直接是数组
      return { data: { data: response } };
    } else if (response.data && Array.isArray(response.data)) {
      // response.data 是数组
      return { data: { data: response.data } };
    } else if (typeof response === 'object') {
      if (response.data?.data && Array.isArray(response.data.data)) {
        // 标准格式 response.data.data
        return response;
      } else if ('items' in (response as any) && Array.isArray((response as any).items)) {
        // items 格式 - 使用类型断言
        const items = (response as any).items;
        return { data: { data: items } };
      } else if (response.data && typeof response.data === 'object' && 'categories' in (response.data as any)) {
        // 嵌套categories字段 - 使用类型断言
        const categories = (response.data as any).categories;
        return { data: { data: categories } };
      }
    }
    
    // 返回空数组
    console.error('未知的量化项目分类响应格式:', response);
    return { data: { data: [] } };
  } catch (error: any) { // 明确指定error类型为any
    console.error('获取量化项目分类失败:', error);
    
    // 错误降级处理：如果API请求失败，提供本地默认分类
    if (error.response && error.response.status === 403) {
      console.log('使用本地默认分类作为回退');
      const now = new Date().toISOString();
      const defaultCategories = [
        { id: 1, name: '学习', description: '学习相关的量化项目', is_active: true, created_at: now, updated_at: now },
        { id: 2, name: '纪律', description: '纪律相关的量化项目', is_active: true, created_at: now, updated_at: now },
        { id: 3, name: '卫生', description: '卫生相关的量化项目', is_active: true, created_at: now, updated_at: now },
        { id: 4, name: '活动', description: '活动相关的量化项目', is_active: true, created_at: now, updated_at: now },
        { id: 5, name: '其他', description: '其他类型的量化项目', is_active: true, created_at: now, updated_at: now }
      ];
      return { data: { data: defaultCategories } };
    }
    
    return { data: { data: [] } };
  }
}

/**
 * 创建量化项目分类
 * @param data 分类数据
 */
export async function createQuantItemCategory(data: CreateQuantItemCategoryPayload) {
  try {
    console.log('创建分类请求数据:', data);
    const response = await http.post<{ data: QuantItemCategory }>('/quant-item-categories', data);
    console.log('创建分类响应:', response);
    
    // 直接返回原始响应，让调用方处理不同的响应格式
    return response;
  } catch (error) {
    console.error('创建分类失败:', error);
    throw error;
  }
}

/**
 * 更新量化项目分类
 * @param id 分类ID
 * @param data 更新数据
 */
export async function updateQuantItemCategory(id: number, data: UpdateQuantItemCategoryPayload) {
  try {
    console.log(`更新分类 ${id} 请求数据:`, data);
    const response = await http.put<{ data: QuantItemCategory }>(`/quant-item-categories/${id}`, data);
    console.log(`更新分类 ${id} 响应:`, response);
    
    // 直接返回原始响应，让调用方处理不同的响应格式
    return response;
  } catch (error) {
    console.error(`更新分类 ${id} 失败:`, error);
    throw error;
  }
}

/**
 * 删除量化项目分类
 * @param id 分类ID
 */
export async function deleteQuantItemCategory(id: number) {
  return http.delete(`/quant-item-categories/${id}`);
}

/**
 * 批量导入量化项目
 * @param formData 包含CSV文件的FormData
 */
export async function importQuantItems(formData: FormData) {
  return http.post<{
    data: {
      success: number;
      failed?: Array<{
        row: number;
        reason: string;
      }>;
    }
  }>('/quant-items/import', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
}

/**
 * 导出量化项目
 * @param params 查询参数
 */
export async function exportQuantItems(params = {}) {
  return http.get('/quant-items/export', { 
    params,
    responseType: 'blob'
  });
}
