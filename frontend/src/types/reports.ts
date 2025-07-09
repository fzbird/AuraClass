/**
 * 报表相关类型定义
 */

/**
 * 报表类型
 */
export type ReportType = 'student' | 'class' | 'all-classes';

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
 * 报表数据接口
 */
export interface ReportData {
  report_type: ReportType;
  template_id?: string;
  generated_at: string;
  metadata: {
    class_name?: string;
    student_name?: string;
    date_range?: {
      start_date: string;
      end_date: string;
    };
  };
  summary: {
    total_records: number;
    total_score: number;
    average_score: number;
  };
  data: {
    student_list?: Array<{
      rank: number;
      student_id: string;
      student_no: string;
      student_name: string;
      total_score: number;
      record_count: number;
    }>;
    record_list?: Array<{
      id: string;
      date: string;
      item_name: string;
      score: number;
      reason: string;
    }>;
    item_distribution?: Array<{
      item_name: string;
      record_count: number;
      total_score: number;
      percentage: number;
    }>;
  };
}

/**
 * 导出报表响应
 */
export interface ExportReportResponse {
  success: boolean;
  file_url?: string;
  message?: string;
} 