/**
 * 班级实体接口
 */
export interface Class {
  id: number;
  name: string;
  grade: string;
  code: string;
  teacher_id?: number;
  teacher_name?: string;
  student_count: number;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

/**
 * 创建班级负载接口
 */
export interface CreateClassPayload {
  name: string;
  grade: string;
  code: string;
  teacher_id?: number;
  description?: string;
  is_active?: boolean;
}

/**
 * 更新班级负载接口
 */
export interface UpdateClassPayload {
  name?: string;
  grade?: string;
  code?: string;
  teacher_id?: number;
  description?: string;
  is_active?: boolean;
}

/**
 * 班级统计数据接口
 */
export interface ClassStatistics {
  id: number;
  name: string;
  student_count: number;
  total_records: number;
  avg_score: number;
  top_students: ClassTopStudent[];
  score_distribution: {
    ranges: string[];
    counts: number[];
  };
}

/**
 * 班级优秀学生接口
 */
export interface ClassTopStudent {
  student_id: number;
  student_name: string;
  total_score: number;
  rank: number;
} 