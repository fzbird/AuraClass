/**
 * 学生实体接口
 */
export interface Student {
  id: number;
  user_id: number | null;
  student_id_no: string;
  full_name: string;
  class_id: number;
  class_name?: string;
  gender: string;
  birth_date?: string;
  phone?: string;
  email?: string;
  contact_info?: string;
  avatar_url?: string;
  total_score?: number;
  rank?: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

/**
 * 创建学生负载接口
 */
export interface CreateStudentPayload {
  student_id_no: string;
  full_name: string;
  class_id: number;
  gender: string;
  birth_date?: string;
  phone?: string;
  email?: string;
  contact_info?: string;
  avatar_url?: string;
  is_active?: boolean;
  user_id?: number | null;
}

/**
 * 更新学生负载接口
 */
export interface UpdateStudentPayload {
  student_id_no?: string;
  full_name?: string;
  class_id?: number;
  gender?: string;
  birth_date?: string;
  phone?: string;
  email?: string;
  contact_info?: string;
  avatar_url?: string;
  total_score?: number;
  rank?: number;
  is_active?: boolean;
  user_id?: number | null;
}

/**
 * 学生统计数据接口
 */
export interface StudentStatistics {
  total: number;
  active: number;
  by_class: ClassDistribution[];
  by_gender: GenderDistribution;
}

/**
 * 班级分布接口
 */
export interface ClassDistribution {
  class_id: number;
  class_name: string;
  count: number;
}

/**
 * 性别分布接口
 */
export interface GenderDistribution {
  male: number;
  female: number;
}

/**
 * 学生量化记录概要接口
 */
export interface StudentRecordSummary {
  student_id: number;
  total_score: number;
  record_count: number;
  latest_record_date: string | null;
  positive_records: number;
  negative_records: number;
}

export interface StudentFilter {
  classId?: number;
  gender?: string;
  search?: string;
  page?: number;
  pageSize?: number;
} 