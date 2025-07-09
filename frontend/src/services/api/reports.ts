/**
 * 报表相关API服务
 */

import http from '../../services/http';
import type { 
  ReportType
} from '@/types/reports';

/**
 * 报表模板接口
 */
export interface ReportTemplate {
  id: string;
  user_id: string;
  name: string;
  type: ReportType;
  description: string;
  content: string;
  created_at: string;
  updated_at: string;
}

/**
 * 创建报表模板的请求载荷
 */
export interface CreateReportTemplatePayload {
  name: string;
  type: ReportType;
  description: string;
  content: string;
}

/**
 * 更新报表模板的请求载荷
 */
export interface UpdateReportTemplatePayload {
  name?: string;
  type?: ReportType;
  description?: string;
  content?: string;
}

/**
 * 报表生成请求载荷
 */
export interface GenerateReportPayload {
  report_type: ReportType;
  template_id?: string;
  class_id?: string;
  student_id?: string;
  date_range?: {
    start_date: string;
    end_date: string;
  };
  include_details?: boolean;
  include_charts?: boolean;
}

/**
 * 导出报表响应
 */
export interface ExportReportResponse {
  success: boolean;
  file_url?: string;
  message?: string;
}

/**
 * 获取报表模板列表
 */
export async function getReportTemplates() {
  return http.get<{ data: ReportTemplate[] }>('/api/report-templates');
}

/**
 * 根据ID获取特定的报表模板
 * 
 * @param id 模板ID
 */
export async function getReportTemplate(id: string) {
  return http.get<{ data: ReportTemplate }>(`/api/report-templates/${id}`);
}

/**
 * 创建新的报表模板
 * 
 * @param payload 创建模板的数据
 */
export async function createReportTemplate(payload: CreateReportTemplatePayload) {
  return http.post<{ data: ReportTemplate }>('/api/report-templates', payload);
}

/**
 * 更新现有的报表模板
 * 
 * @param id 模板ID
 * @param payload 更新的数据
 */
export async function updateReportTemplate(id: string, payload: UpdateReportTemplatePayload) {
  return http.put<{ data: ReportTemplate }>(`/api/report-templates/${id}`, payload);
}

/**
 * 删除报表模板
 * 
 * @param id 模板ID
 */
export async function deleteReportTemplate(id: string) {
  return http.delete(`/api/report-templates/${id}`);
}

/**
 * 生成报表数据
 * 
 * @param payload 报表生成参数
 */
export async function generateReportData(payload: GenerateReportPayload) {
  return http.post<{ data: any }>('/api/reports/generate', payload);
}

/**
 * 导出报表为PDF
 * 
 * @param payload 报表生成参数
 */
export async function exportReportPdf(payload: GenerateReportPayload) {
  return http.post<ExportReportResponse>('/api/reports/export-pdf', payload, {
    responseType: 'blob'
  });
} 