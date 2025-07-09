import http from '../http';
import type { PaginatedResponse } from '@/types/common';
import type { Student, StudentStatistics, CreateStudentPayload, UpdateStudentPayload } from '@/types/student';

/**
 * 获取学生列表
 * @param params 查询参数
 */
export async function getStudents(params = {}) {
  try {
    const response = await http.get<PaginatedResponse<Student>>('/students', { params });
    
    // 添加调试输出
    console.log('学生数据响应:', response);
    console.log('学生数据响应类型:', typeof response);
    console.log('学生数据响应键:', Object.keys(response));
    
    // 更灵活地解析不同的响应格式
    if (Array.isArray(response)) {
      // 直接是数组
      return { data: { data: response } };
    } else if (response.data && Array.isArray(response.data)) {
      // response.data 是数组
      return { data: { data: response.data } };
    } else if (response.data?.data && Array.isArray(response.data.data)) {
      // 标准格式
      return response;
    } else {
      console.error('未知的学生数据响应格式:', response);
      return { data: { data: [] } };
    }
  } catch (error) {
    console.error('获取学生数据失败:', error);
    return { data: { data: [] } };
  }
}

/**
 * 获取单个学生详情
 * @param id 学生ID
 */
export async function getStudent(id: number) {
  try {
    const response = await http.get<any>(`/students/${id}`);
    console.log('获取学生详情原始响应:', response);
    
    // 处理可能的不同响应格式
    if (response.data) {
      // 标准格式：{ data: Student }
      return { data: response.data };
    } else if (response.id) {
      // 直接返回学生对象格式
      return { data: response };
    } else {
      console.error('未知的学生详情响应格式:', response);
      return { data: {} };
    }
  } catch (error) {
    console.error('获取学生详情失败:', error);
    throw error;
  }
}

/**
 * 创建学生
 * @param data 学生数据
 */
export async function createStudent(data: CreateStudentPayload) {
  return http.post<{ data: Student }>('/students', data);
}

/**
 * 更新学生信息
 * @param id 学生ID
 * @param data 更新的学生数据
 */
export async function updateStudent(id: number, data: UpdateStudentPayload) {
  return http.put<{ data: Student }>(`/students/${id}`, data);
}

/**
 * 获取学生的量化记录
 * @param id 学生ID
 * @param params 查询参数
 */
export async function getStudentRecords(id: number, params = {}) {
  try {
    const response = await http.get<any>(`/students/${id}/records`, { params });
    console.log('获取学生记录原始响应:', response);
    
    // 处理可能的不同响应格式
    if (Array.isArray(response.data)) {
      // 标准格式：{ data: [...records] }
      return { data: response.data };
    } else if (Array.isArray(response)) {
      // 直接返回数组格式
      return { data: response };
    } else {
      console.error('未知的学生记录响应格式:', response);
      return { data: [] };
    }
  } catch (error) {
    console.error('获取学生记录失败:', error);
    return { data: [] };
  }
}

/**
 * 获取学生的量化统计
 * @param id 学生ID
 */
export async function getStudentStatistics(id: number) {
  return http.get<{ data: any }>(`/students/${id}/statistics`);
}

/**
 * 批量导入学生
 * @param students 学生数据数组
 */
export async function importStudents(students: CreateStudentPayload[]) {
  // 由于后端没有提供批量导入端点，改为使用单次循环导入方式
  const results = {
    success: 0,
    failed: 0,
    failedRecords: [] as Array<{
      data: Partial<CreateStudentPayload>;
      reason: string;
    }>
  };

  // 逐个创建学生
  for (const student of students) {
    try {
      // 格式化日期为ISO格式 (YYYY-MM-DD)
      const formattedStudent = {
        ...student,
      };
      
      // 处理出生日期格式
      if (formattedStudent.birth_date) {
        // 尝试标准化日期格式
        try {
          // 处理不同的日期分隔符（斜杠、点、短横线等）
          const dateStr = formattedStudent.birth_date.toString().trim();
          const dateParts = dateStr.split(/[\/\.\-]/);
          
          if (dateParts.length === 3) {
            const year = dateParts[0].padStart(4, '0');
            const month = dateParts[1].padStart(2, '0');
            const day = dateParts[2].padStart(2, '0');
            
            // 使用ISO格式 (YYYY-MM-DD)
            formattedStudent.birth_date = `${year}-${month}-${day}`;
          }
        } catch (error) {
          console.warn('无法解析日期:', formattedStudent.birth_date);
        }
      }
      
      await createStudent(formattedStudent);
      results.success++;
    } catch (error: any) {
      results.failed++;
      results.failedRecords.push({
        data: student,
        reason: error.response?.data?.error?.detail || 
               error.response?.data?.error?.message ||
               (error.response?.data?.error?.details?.[0]?.msg ? 
                `字段 ${error.response?.data?.error?.details?.[0]?.loc[1]}: ${error.response?.data?.error?.details?.[0]?.msg}` : 
                error.message) || 
               '创建失败'
      });
    }
  }

  // 返回与原接口相同结构的响应
  return {
    data: {
      success: results.success,
      imported: results.success,
      failed: results.failed,
      failedRecords: results.failedRecords
    }
  };
}

/**
 * 导出学生数据
 * @param params 筛选参数
 */
export async function exportStudents(params = {}) {
  return http.get('/students/export', { 
    params,
    responseType: 'blob'
  });
}

/**
 * 切换学生活跃状态
 * @param id 学生ID
 * @param active 是否活跃
 */
export async function toggleStudentActive(id: number, active: boolean) {
  return http.patch<{ data: Student }>(`/students/${id}/active`, null, { params: { active } });
}

/**
 * 更新学生分数和排名
 * @param classId 可选班级ID
 */
export async function updateStudentScores(classId?: number) {
  const data = classId ? { class_id: classId } : {};
  return http.post<{ 
    success: boolean;
    message: string;
    updated_count: number;
  }>('/students/update-scores', data);
}

/**
 * 删除学生
 * @param id 学生ID
 */
export async function deleteStudent(id: number) {
  return http.delete(`/students/${id}`);
}

/**
 * 强制删除学生及其所有量化记录
 * @param id 学生ID
 */
export async function forceDeleteStudent(id: number) {
  return http.delete<{ data: { success: boolean; message: string; deleted_records_count: number } }>(`/students/${id}/force`);
}
