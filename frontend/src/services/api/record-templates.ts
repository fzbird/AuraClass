import http from '../http';
import type { RecordTemplate, CreateRecordTemplatePayload } from '@/types/record-template';

/**
 * 获取记录模板列表
 * @param params 查询参数
 */
export async function getRecordTemplates(params = {}) {
  return http.get<{ data: RecordTemplate[] }>('/record-templates', { params });
}

/**
 * 获取记录模板详情
 * @param id 模板ID
 */
export async function getRecordTemplate(id: number) {
  return http.get<{ data: RecordTemplate }>(`/record-templates/${id}`);
}

/**
 * 创建记录模板
 * @param data 模板数据
 */
export async function createRecordTemplate(data: CreateRecordTemplatePayload) {
  return http.post<{ data: RecordTemplate }>('/record-templates', data);
}

/**
 * 更新记录模板
 * @param id 模板ID
 * @param data 更新数据
 */
export async function updateRecordTemplate(id: number, data: Partial<CreateRecordTemplatePayload>) {
  return http.put<{ data: RecordTemplate }>(`/record-templates/${id}`, data);
}

/**
 * 删除记录模板
 * @param id 模板ID
 */
export async function deleteRecordTemplate(id: number) {
  return http.delete<{ success: boolean }>(`/record-templates/${id}`);
} 