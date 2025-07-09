import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { 
  getQuantRecords, 
  getQuantRecord, 
  createQuantRecord, 
  updateQuantRecord, 
  deleteQuantRecord,
  exportQuantRecords,
  importQuantRecords,
  getQuantRecordsStatistics
} from '@/services/api/records';
import type { 
  QuantRecord, 
  CreateQuantRecordPayload, 
  UpdateQuantRecordPayload, 
  QuantRecordFilter, 
  QuantRecordStatistics 
} from '@/types/record';
import type { PaginatedResponse } from '@/types/common';

export const useRecordStore = defineStore('record', () => {
  // 状态
  const records = ref<QuantRecord[]>([]);
  const currentRecord = ref<QuantRecord | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const pagination = ref({
    page: 1,
    pageSize: 10,
    total: 0
  });
  const filters = ref<QuantRecordFilter>({});
  const sorting = ref({
    field: 'record_date',
    order: 'descend' as 'ascend' | 'descend' | null
  });
  const statistics = ref<QuantRecordStatistics | null>(null);

  // 计算属性
  const totalPages = computed(() => {
    return Math.ceil(pagination.value.total / pagination.value.pageSize);
  });

  const hasRecords = computed(() => {
    return records.value.length > 0;
  });

  // 方法
  async function fetchRecords() {
    loading.value = true;
    error.value = null;

    try {
      const response = await getQuantRecords({
        page: pagination.value.page,
        page_size: pagination.value.pageSize,
        sort_field: sorting.value.field,
        sort_order: sorting.value.order,
        ...filters.value
      });
      
      const paginatedData = response.data as PaginatedResponse<QuantRecord>;
      records.value = paginatedData.data || [];
      
      if (paginatedData.meta && paginatedData.meta.pagination) {
        pagination.value.total = paginatedData.meta.pagination.total || 0;
      }
    } catch (err) {
      console.error('Failed to fetch records:', err);
      error.value = err instanceof Error ? err.message : String(err);
    } finally {
      loading.value = false;
    }
  }

  async function fetchRecordById(id: number) {
    loading.value = true;
    error.value = null;

    try {
      const response = await getQuantRecord(id);
      currentRecord.value = response.data.data;
      return currentRecord.value;
    } catch (err) {
      console.error(`Failed to fetch record with ID ${id}:`, err);
      error.value = err instanceof Error ? err.message : String(err);
      return null;
    } finally {
      loading.value = false;
    }
  }

  async function addRecord(recordData: CreateQuantRecordPayload) {
    loading.value = true;
    error.value = null;

    try {
      const response = await createQuantRecord(recordData);
      const newRecord = response.data.data;
      
      // 更新记录列表
      records.value.unshift(newRecord);
      pagination.value.total += 1;
      
      return newRecord;
    } catch (err) {
      console.error('Failed to create record:', err);
      error.value = err instanceof Error ? err.message : String(err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function editRecord(id: number, recordData: UpdateQuantRecordPayload) {
    loading.value = true;
    error.value = null;

    try {
      const response = await updateQuantRecord(id, recordData);
      const updatedRecord = response.data.data;
      
      // 更新列表中的记录
      const index = records.value.findIndex(record => record.id === id);
      if (index !== -1) {
        records.value[index] = updatedRecord;
      }
      
      // 更新当前记录（如果正在查看）
      if (currentRecord.value && currentRecord.value.id === id) {
        currentRecord.value = updatedRecord;
      }
      
      return updatedRecord;
    } catch (err) {
      console.error(`Failed to update record with ID ${id}:`, err);
      error.value = err instanceof Error ? err.message : String(err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function removeRecord(id: number) {
    loading.value = true;
    error.value = null;

    try {
      await deleteQuantRecord(id);
      
      // 从列表中移除
      records.value = records.value.filter(record => record.id !== id);
      pagination.value.total -= 1;
      
      // 如果删除的是当前正在查看的记录，清空当前记录
      if (currentRecord.value && currentRecord.value.id === id) {
        currentRecord.value = null;
      }
      
      return true;
    } catch (err) {
      console.error(`Failed to delete record with ID ${id}:`, err);
      error.value = err instanceof Error ? err.message : String(err);
      return false;
    } finally {
      loading.value = false;
    }
  }

  async function exportRecords(format: 'csv' | 'excel' = 'excel') {
    loading.value = true;
    error.value = null;

    try {
      return await exportQuantRecords({
        format,
        ...filters.value
      });
    } catch (err) {
      console.error('Failed to export records:', err);
      error.value = err instanceof Error ? err.message : String(err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function importRecords(file: File) {
    loading.value = true;
    error.value = null;

    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await importQuantRecords(formData);
      // 刷新记录列表
      await fetchRecords();
      
      return response.data.data;
    } catch (err) {
      console.error('Failed to import records:', err);
      error.value = err instanceof Error ? err.message : String(err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function fetchStatistics() {
    loading.value = true;
    error.value = null;

    try {
      const response = await getQuantRecordsStatistics(filters.value);
      statistics.value = response.data.data;
      return statistics.value;
    } catch (err) {
      console.error('Failed to fetch record statistics:', err);
      error.value = err instanceof Error ? err.message : String(err);
      return null;
    } finally {
      loading.value = false;
    }
  }

  // 分页和筛选方法
  function setPage(page: number) {
    pagination.value.page = page;
    fetchRecords();
  }

  function setPageSize(size: number) {
    pagination.value.pageSize = size;
    pagination.value.page = 1; // 重置为第一页
    fetchRecords();
  }

  function setFilters(newFilters: QuantRecordFilter) {
    filters.value = { ...newFilters };
    pagination.value.page = 1; // 重置为第一页
    fetchRecords();
  }

  function setSorting(field: string, order: 'ascend' | 'descend' | null = 'descend') {
    sorting.value.field = field;
    sorting.value.order = order;
    fetchRecords();
  }

  function reset() {
    records.value = [];
    currentRecord.value = null;
    pagination.value = {
      page: 1,
      pageSize: 10,
      total: 0
    };
    filters.value = {};
    sorting.value = {
      field: 'record_date',
      order: 'descend'
    };
    error.value = null;
    statistics.value = null;
  }

  return {
    // 状态
    records,
    currentRecord,
    loading,
    error,
    pagination,
    filters,
    sorting,
    statistics,
    
    // 计算属性
    totalPages,
    hasRecords,
    
    // 方法
    fetchRecords,
    fetchRecordById,
    addRecord,
    editRecord,
    removeRecord,
    exportRecords,
    importRecords,
    fetchStatistics,
    setPage,
    setPageSize,
    setFilters,
    setSorting,
    reset
  };
}); 