export interface CategoryStat {
  category: string;
  count: number;
  score: number;
  average: number;
}

export interface StatisticsSummary {
  total_students: number;
  total_items: number;
  total_records: number;
  total_score: number;
  monthly_records: number;
  average_score: number;
  categories: CategoryStat[];
  itemDistribution?: ItemDistribution[];
  students_with_records: number;
  positive_percentage: number;
  negative_percentage: number;
  neutral_percentage: number;
}

export interface TimeSeriesPoint {
  date: string;
  count: number;
  score: number;
  average: number;
}

export interface StudentRanking {
  id: number;
  student_id_no: string;
  full_name: string;
  class_id: number;
  class_name: string;
  total_score: number;
  record_count: number;
  average_score: number;
}

export interface ClassComparison {
  class_id: number;
  class_name: string;
  student_count: number;
  record_count: number;
  total_score: number;
  average_score: number;
  categories: CategoryStat[];
}

export interface TimelineParams {
  interval?: 'day' | 'week' | 'month';
  start_date?: string;
  end_date?: string;
  class_id?: number;
  category?: string;
}

/**
 * 班级统计数据
 */
export interface ClassStatisticsData {
  // 总体统计
  total_records: number;
  total_score: number;
  average_score: number;
  positive_records: number;
  negative_records: number;
  students_with_records: number;
  total_students: number;
  
  // 日期分布
  date_distribution: {
    date: string;
    count: number;
    score_sum: number;
  }[];
  
  // 项目分布
  item_distribution: {
    item_id: number;
    item_name: string;
    category?: string;
    count: number;
    score_sum: number;
  }[];
  
  // 班级分布（如果没有指定班级）
  class_distribution?: {
    class_id: number;
    class_name: string;
    record_count: number;
    total_score: number;
    student_count: number;
  }[];
}

/**
 * 学生排名项
 */
export interface StudentRankingItem {
  id: number;
  student_id?: number;
  student_id_no: string;
  name: string;
  class_id: number;
  class_name: string;
  total_score: number;
  record_count: number;
  average_score: number;
  rank: number;
}

/**
 * 量化记录趋势数据
 */
export interface RecordTrend {
  period: string;
  record_count: number;
  score_sum: number;
  average_score: number;
}

/**
 * 统计看板过滤条件
 */
export interface StatisticsDashboardFilter {
  class_id?: number;
  student_id?: number;
  item_id?: number;
  start_date?: string;
  end_date?: string;
  period?: 'day' | 'week' | 'month';
}

/**
 * 班级统计接口
 */
export interface ClassStatistics {
  id: number;
  name: string;
  student_count: number;
  total_score: number;
  record_count: number;
  average_score: number;
  rank: number;
}

/**
 * 项目分布接口
 */
export interface ItemDistribution {
  item_id: number;
  item_name: string;
  category?: string;
  count: number;
  score_sum: number;
  percentage: number;
} 