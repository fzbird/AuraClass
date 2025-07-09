import type { StatisticsSummary, RecordTrend, StudentRankingItem, ClassStatistics } from '@/types/statistics';

/**
 * 生成模拟的统计摘要数据
 */
export function getMockStatisticsSummary(): { data: StatisticsSummary } {
  return {
    data: {
      total_students: 150,
      total_items: 28,
      total_records: 1250,
      total_score: 3750,
      monthly_records: 450,
      average_score: 3.0,
      students_with_records: 130,
      positive_percentage: 70,
      negative_percentage: 20,
      neutral_percentage: 10,
      categories: [
        { name: '学习', count: 500, score_sum: 1500 },
        { name: '纪律', count: 350, score_sum: 1050 },
        { name: '卫生', count: 200, score_sum: 600 },
        { name: '德育', count: 200, score_sum: 600 }
      ]
    }
  };
}

/**
 * 生成模拟的趋势数据
 */
export function getMockTrendData(interval: string = 'day'): { data: RecordTrend[] } {
  const data: RecordTrend[] = [];
  const days = interval === 'day' ? 30 : (interval === 'week' ? 12 : 6);
  
  for (let i = 0; i < days; i++) {
    const date = new Date();
    date.setDate(date.getDate() - i);
    const period = formatPeriod(date, interval);
    
    data.push({
      period,
      record_count: Math.floor(Math.random() * 30) + 10,
      score_sum: Math.floor(Math.random() * 90) + 30,
      average_score: (Math.random() * 4 + 1).toFixed(1) as unknown as number
    });
  }
  
  return { data: data.reverse() };
}

/**
 * 生成模拟的班级列表
 */
export function getMockClasses() {
  return {
    data: [
      { id: 1, name: '初一(1)班', grade: '初一', student_count: 45 },
      { id: 2, name: '初一(2)班', grade: '初一', student_count: 43 },
      { id: 3, name: '初二(1)班', grade: '初二', student_count: 46 },
      { id: 4, name: '初二(2)班', grade: '初二', student_count: 44 }
    ],
    meta: {
      pagination: {
        page: 1,
        size: 10,
        total: 4
      }
    }
  };
}

/**
 * 生成模拟的量化项目列表
 */
export function getMockQuantItems() {
  return {
    data: [
      { id: 1, name: '按时完成作业', category: '学习', score: 2 },
      { id: 2, name: '课堂发言积极', category: '学习', score: 1 },
      { id: 3, name: '迟到', category: '纪律', score: -2 },
      { id: 4, name: '违反纪律', category: '纪律', score: -3 },
      { id: 5, name: '清扫责任区', category: '卫生', score: 2 },
      { id: 6, name: '参与志愿活动', category: '德育', score: 3 }
    ],
    meta: {
      pagination: {
        page: 1,
        size: 10,
        total: 6
      }
    }
  };
}

/**
 * 生成模拟的学生排名
 */
export function getMockStudentRankings(): { data: StudentRankingItem[] } {
  const students: StudentRankingItem[] = [];
  
  for (let i = 1; i <= 10; i++) {
    students.push({
      id: i,
      student_id_no: `S${10000 + i}`,
      full_name: `学生${i}`,
      class_name: `初一(${Math.ceil(i/5)})班`,
      total_score: 100 - (i * 5) + Math.floor(Math.random() * 10),
      rank: i,
      record_count: 30 - Math.floor(i/2),
      class_id: Math.ceil(i/5)
    });
  }
  
  return { data: students };
}

// 辅助函数：根据时间间隔格式化周期
function formatPeriod(date: Date, interval: string): string {
  const year = date.getFullYear();
  const month = date.getMonth() + 1;
  const day = date.getDate();
  
  if (interval === 'day') {
    return `${year}-${month.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`;
  } else if (interval === 'week') {
    // 简化版，实际应使用更复杂的周计算
    return `${year}年第${Math.ceil(day/7) + (month-1)*4}周`;
  } else {
    return `${year}-${month.toString().padStart(2, '0')}`;
  }
} 