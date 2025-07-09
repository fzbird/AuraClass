import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { 
  getClasses, 
  getClass, 
  createClass, 
  updateClass, 
  deleteClass,
  getClassStatistics,
  getClassStudents 
} from '@/services/api/classes';
import type { Class, CreateClassPayload, UpdateClassPayload } from '@/types/class';
import type { PaginatedResponse } from '@/types/common';

interface ClassStatistics {
  studentCount: number;
  recordCount: number;
  averageScore: number;
  positivePercent: number;
  negativePercent: number;
  topStudents: Array<{
    id: number;
    name: string;
    score: number;
  }>;
}

export const useClassStore = defineStore('class', () => {
  // 状态
  const classes = ref<Class[]>([]);
  const currentClass = ref<Class | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const pagination = ref({
    page: 1,
    pageSize: 10,
    total: 0
  });
  const filters = ref({
    name: '',
    gradeLevel: null,
    teacherId: null
  });
  const sortBy = ref('');
  const sortOrder = ref('asc');
  const statistics = ref<ClassStatistics | null>(null);

  // 计算属性
  const totalPages = computed(() => {
    return Math.ceil(pagination.value.total / pagination.value.pageSize);
  });

  const hasClasses = computed(() => {
    return classes.value.length > 0;
  });

  // 方法
  async function fetchClasses() {
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

      const response = await getClasses(params);
      const paginatedData = response.data as PaginatedResponse<Class>;
      classes.value = paginatedData.data || [];
      
      if (paginatedData.meta && paginatedData.meta.pagination) {
        pagination.value.total = paginatedData.meta.pagination.total || 0;
      }
    } catch (err) {
      console.error('Failed to fetch classes:', err);
      error.value = '获取班级列表失败';
    } finally {
      loading.value = false;
    }
  }

  async function fetchClassById(id: number) {
    loading.value = true;
    error.value = null;

    try {
      const response = await getClass(id);
      currentClass.value = response.data.data;
      return response.data.data;
    } catch (err) {
      console.error(`Failed to fetch class with ID ${id}:`, err);
      error.value = '获取班级详情失败';
      return null;
    } finally {
      loading.value = false;
    }
  }

  async function addClass(classData: CreateClassPayload) {
    loading.value = true;
    error.value = null;

    try {
      const response = await createClass(classData);
      await fetchClasses();
      return response.data.data;
    } catch (err) {
      console.error('Failed to create class:', err);
      error.value = '创建班级失败';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function editClass(id: number, classData: UpdateClassPayload) {
    loading.value = true;
    error.value = null;

    try {
      const response = await updateClass(id, classData);
      const updatedClass = response.data.data;
      
      // 更新当前班级（如果正在查看）
      if (currentClass.value && currentClass.value.id === id) {
        currentClass.value = updatedClass;
      }
      
      // 更新列表中的班级
      const index = classes.value.findIndex(c => c.id === id);
      if (index !== -1) {
        classes.value[index] = updatedClass;
      }
      
      return updatedClass;
    } catch (err) {
      console.error(`Failed to update class with ID ${id}:`, err);
      error.value = '更新班级信息失败';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function removeClass(id: number) {
    loading.value = true;
    error.value = null;

    try {
      await deleteClass(id);
      
      // 如果删除的是当前正在查看的班级，清空当前班级
      if (currentClass.value && currentClass.value.id === id) {
        currentClass.value = null;
      }
      
      // 从列表中移除
      classes.value = classes.value.filter(c => c.id !== id);
      pagination.value.total -= 1;
      
      return true;
    } catch (err) {
      console.error(`Failed to delete class with ID ${id}:`, err);
      error.value = '删除班级失败';
      return false;
    } finally {
      loading.value = false;
    }
  }

  async function fetchClassStudents(classId: number, params = {}) {
    loading.value = true;
    error.value = null;

    try {
      const response = await getClassStudents(classId, params);
      return response.data;
    } catch (err) {
      console.error(`Failed to fetch students for class ${classId}:`, err);
      error.value = '获取班级学生列表失败';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function fetchStatistics(classId: number) {
    loading.value = true;
    error.value = null;

    try {
      if (!classId && currentClass.value) {
        classId = currentClass.value.id;
      }
      
      if (!classId) {
        throw new Error('No class ID provided for statistics');
      }
      
      const response = await getClassStatistics(classId);
      statistics.value = response.data.data;
      return response.data.data;
    } catch (err) {
      console.error('Failed to fetch class statistics:', err);
      error.value = '获取班级统计数据失败';
      return null;
    } finally {
      loading.value = false;
    }
  }

  // 分页和筛选方法
  function setPage(page: number) {
    pagination.value.page = page;
    fetchClasses();
  }

  function setPageSize(size: number) {
    pagination.value.pageSize = size;
    pagination.value.page = 1; // 重置为第一页
    fetchClasses();
  }

  function setFilters(newFilters: typeof filters.value) {
    filters.value = { ...newFilters };
    pagination.value.page = 1; // 重置为第一页
    fetchClasses();
  }

  function setSorting(field: string, order: 'asc' | 'desc' = 'asc') {
    sortBy.value = field;
    sortOrder.value = order;
    fetchClasses();
  }

  function reset() {
    classes.value = [];
    currentClass.value = null;
    pagination.value = {
      page: 1,
      pageSize: 10,
      total: 0
    };
    filters.value = {
      name: '',
      gradeLevel: null,
      teacherId: null
    };
    sortBy.value = '';
    sortOrder.value = 'asc';
    error.value = null;
    statistics.value = null;
  }

  return {
    // 状态
    classes,
    currentClass,
    loading,
    error,
    pagination,
    filters,
    sortBy,
    sortOrder,
    statistics,
    
    // 计算属性
    totalPages,
    hasClasses,
    
    // 方法
    fetchClasses,
    fetchClassById,
    addClass,
    editClass,
    removeClass,
    fetchClassStudents,
    fetchStatistics,
    setPage,
    setPageSize,
    setFilters,
    setSorting,
    reset
  };
}); 