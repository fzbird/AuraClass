/**
 * 量化记录基础类型
 */
export interface QuantRecordBase {
  student_id: number;
  item_id: number;
  score: number;
  reason: string;
  record_date: string;
}

/**
 * 量化记录详情，包含关联数据
 */
export interface QuantRecord extends QuantRecordBase {
  id: number;
  recorder_id: number;
  created_at: string;
  updated_at: string;
  
  // 关联数据
  student_name?: string;
  item_name?: string;
  recorder_name?: string;
}

/**
 * 创建量化记录的请求数据
 */
export interface CreateQuantRecordPayload {
  student_id: number;
  item_id: number;
  score: number;
  reason: string;
  record_date: string;
}

/**
 * 更新量化记录的请求数据
 */
export interface UpdateQuantRecordPayload {
  score?: number;
  reason?: string;
  record_date?: string;
}

/**
 * 量化记录过滤参数接口
 */
export interface QuantRecordFilter {
  student_id?: number | number[];
  student_name?: string;
  class_id?: number | number[];
  item_id?: number | number[];
  category?: string;
  min_score?: number;
  max_score?: number;
  start_date?: string;
  end_date?: string;
  recorder_id?: number;
}

/**
 * 量化记录统计接口
 */
export interface QuantRecordStatistics {
  total_records: number;
  total_score: number;
  average_score: number;
  positive_records: number;
  negative_records: number;
  by_date: DateDistribution[];
  by_item: ItemDistribution[];
}

/**
 * 按日期分布接口
 */
export interface DateDistribution {
  date: string;
  count: number;
  score_sum: number;
}

/**
 * 按项目分布接口
 */
export interface ItemDistribution {
  item_id: number;
  item_name: string;
  count: number;
  score_sum: number;
}

/**
 * 学生量化记录摘要接口
 */
export interface StudentRecordSummary {
  student_id: number;
  student_name: string;
  student_id_no: string;
  class_name: string;
  total_score: number;
  record_count: number;
  rank: number;
}

/**
 * 量化记录模板接口
 */
export interface RecordTemplate {
  id: number;
  user_id: number;
  name: string;
  item_id: number;
  item_name: string;
  score: number;
  reason: string;
  description?: string;
  created_at: string;
  updated_at: string;
} 