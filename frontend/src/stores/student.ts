import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { 
  getStudents, 
  getStudent, 
  createStudent, 
  updateStudent, 
  deleteStudent, 
  getStudentRecords,
  importStudents,
  exportStudents,
  getStudentStatistics,
  toggleStudentActive,
  updateStudentScores
} from '@/services/api/students';
import type { Student, CreateStudentPayload, UpdateStudentPayload } from '@/types/student';
import type { PaginatedResponse } from '@/types/common';

export const useStudentStore = defineStore('student', () => {
  // 状态
  const students = ref<Student[]>([]);
  const currentStudent = ref<Student | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const pagination = ref({
    page: 1,
    pageSize: 10,
    total: 0
  });
  const filters = ref({
    name: '',
    classId: null,
    status: null
  });
  const sortBy = ref('');
  const sortOrder = ref('asc');
  const statistics = ref<{
    total: number;
    active: number;
    byClass: Array<{classId: number; className: string; count: number}>;
    byGender: {male: number; female: number};
  } | null>(null);

  // 计算属性
  const totalPages = computed(() => {
    return Math.ceil(pagination.value.total / pagination.value.pageSize);
  });

  const hasStudents = computed(() => {
    return students.value.length > 0;
  });

  // 操作方法
  async function fetchStudents() {
    loading.value = true;
    error.value = null;

    try {
      const params: Record<string, any> = {
        page: pagination.value.page,
        size: pagination.value.pageSize,
        ...filters.value
      };

      if (sortBy.value) {
        params.sort_by = sortBy.value;
        params.sort_order = sortOrder.value;
      }

      const response = await getStudents(params);
      const paginatedData = response.data as PaginatedResponse<Student>;
      students.value = paginatedData.data || [];
      
      if (paginatedData.meta && paginatedData.meta.pagination) {
        pagination.value.total = paginatedData.meta.pagination.total || 0;
      }
    } catch (err) {
      console.error('Failed to fetch students:', err);
      error.value = '获取学生列表失败';
    } finally {
      loading.value = false;
    }
  }

  async function fetchStudentById(id: number) {
    loading.value = true;
    error.value = null;

    try {
      const response = await getStudent(id);
      currentStudent.value = response.data.data;
      return response.data.data;
    } catch (err) {
      console.error(`Failed to fetch student with ID ${id}:`, err);
      error.value = '获取学生详情失败';
      return null;
    } finally {
      loading.value = false;
    }
  }

  async function addStudent(studentData: CreateStudentPayload) {
    loading.value = true;
    error.value = null;

    try {
      const response = await createStudent(studentData);
      // 刷新学生列表
      await fetchStudents();
      return response.data.data;
    } catch (err) {
      console.error('Failed to create student:', err);
      error.value = '创建学生失败';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function editStudent(id: number, studentData: UpdateStudentPayload) {
    loading.value = true;
    error.value = null;

    try {
      const response = await updateStudent(id, studentData);
      const updatedStudent = response.data.data;
      
      // 更新当前学生（如果正在查看）
      if (currentStudent.value && currentStudent.value.id === id) {
        currentStudent.value = updatedStudent;
      }
      
      // 更新列表中的学生
      const index = students.value.findIndex(s => s.id === id);
      if (index !== -1) {
        students.value[index] = updatedStudent;
      }
      
      return updatedStudent;
    } catch (err) {
      console.error(`Failed to update student with ID ${id}:`, err);
      error.value = '更新学生信息失败';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function removeStudent(id: number) {
    loading.value = true;
    error.value = null;

    try {
      await deleteStudent(id);
      
      // 如果删除的是当前正在查看的学生，清空当前学生
      if (currentStudent.value && currentStudent.value.id === id) {
        currentStudent.value = null;
      }
      
      // 从列表中移除
      students.value = students.value.filter(s => s.id !== id);
      pagination.value.total -= 1;
      
      return true;
    } catch (err) {
      console.error(`Failed to delete student with ID ${id}:`, err);
      error.value = '删除学生失败';
      return false;
    } finally {
      loading.value = false;
    }
  }

  async function toggleActiveStudent(id: number, active: boolean) {
    loading.value = true;
    error.value = null;

    try {
      const response = await toggleStudentActive(id, active);
      const updatedStudent = response.data.data;
      
      // 更新当前学生（如果正在查看）
      if (currentStudent.value && currentStudent.value.id === id) {
        currentStudent.value = updatedStudent;
      }
      
      // 更新列表中的学生
      const index = students.value.findIndex(s => s.id === id);
      if (index !== -1) {
        students.value[index] = updatedStudent;
      }
      
      return updatedStudent;
    } catch (err) {
      console.error(`Failed to toggle active status for student with ID ${id}:`, err);
      error.value = '更新学生状态失败';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function updateStudentScoresAndRanks(classId?: number) {
    loading.value = true;
    error.value = null;

    try {
      const response = await updateStudentScores(classId);
      // 刷新学生列表以获取更新后的分数和排名
      await fetchStudents();
      return response.data;
    } catch (err) {
      console.error('Failed to update student scores:', err);
      error.value = '更新学生分数和排名失败';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function fetchStudentRecords(studentId: number, params = {}) {
    loading.value = true;
    error.value = null;

    try {
      const response = await getStudentRecords(studentId, params);
      return response.data;
    } catch (err) {
      console.error(`Failed to fetch records for student ${studentId}:`, err);
      error.value = '获取学生量化记录失败';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function importStudentData(data: CreateStudentPayload[]) {
    loading.value = true;
    error.value = null;

    try {
      const response = await importStudents(data);
      // 刷新学生列表
      await fetchStudents();
      return response.data.data;
    } catch (err) {
      console.error('Failed to import students:', err);
      error.value = '导入学生数据失败';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function exportStudentData(params = {}) {
    loading.value = true;
    error.value = null;

    try {
      return await exportStudents({
        ...params,
        ...filters.value
      });
    } catch (err) {
      console.error('Failed to export students:', err);
      error.value = '导出学生数据失败';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function fetchStatistics() {
    loading.value = true;
    error.value = null;

    try {
      const response = await getStudentStatistics(0);
      const statsData = response.data.data;
      
      statistics.value = {
        total: statsData.total,
        active: statsData.active,
        byClass: statsData.by_class.map((c: {class_id: number; class_name: string; count: number}) => ({
          classId: c.class_id,
          className: c.class_name,
          count: c.count
        })),
        byGender: statsData.by_gender
      };
      
      return statistics.value;
    } catch (err) {
      console.error('Failed to fetch student statistics:', err);
      error.value = '获取学生统计数据失败';
      return null;
    } finally {
      loading.value = false;
    }
  }

  // 分页和筛选方法
  function setPage(page: number) {
    pagination.value.page = page;
    fetchStudents();
  }

  function setPageSize(size: number) {
    pagination.value.pageSize = size;
    pagination.value.page = 1; // 重置为第一页
    fetchStudents();
  }

  function setFilters(newFilters: typeof filters.value) {
    filters.value = { ...newFilters };
    pagination.value.page = 1; // 重置为第一页
    fetchStudents();
  }

  function setSorting(field: string, order: 'asc' | 'desc' = 'asc') {
    sortBy.value = field;
    sortOrder.value = order;
    fetchStudents();
  }

  function reset() {
    students.value = [];
    currentStudent.value = null;
    pagination.value = {
      page: 1,
      pageSize: 10,
      total: 0
    };
    filters.value = {
      name: '',
      classId: null,
      status: null
    };
    sortBy.value = '';
    sortOrder.value = 'asc';
    error.value = null;
  }

  return {
    // 状态
    students,
    currentStudent,
    loading,
    error,
    pagination,
    filters,
    sortBy,
    sortOrder,
    statistics,
    
    // 计算属性
    totalPages,
    hasStudents,
    
    // 方法
    fetchStudents,
    fetchStudentById,
    addStudent,
    editStudent,
    removeStudent,
    toggleActiveStudent,
    updateStudentScoresAndRanks,
    fetchStudentRecords,
    importStudentData,
    exportStudentData,
    fetchStatistics,
    setPage,
    setPageSize,
    setFilters,
    setSorting,
    reset
  };
}); 