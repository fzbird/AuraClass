import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { 
  getQuantItems, 
  getQuantItem, 
  createQuantItem, 
  updateQuantItem, 
  deleteQuantItem,
  getQuantItemCategories,
  createQuantItemCategory,
  updateQuantItemCategory,
  deleteQuantItemCategory,
  importQuantItems,
  exportQuantItems
} from '@/services/api/quant-items';
import type { 
  QuantItem, 
  CreateQuantItemPayload, 
  UpdateQuantItemPayload, 
  QuantItemFilter,
  QuantItemCategory,
  CreateQuantItemCategoryPayload,
  UpdateQuantItemCategoryPayload
} from '@/types/quant-item';
import type { PaginatedResponse } from '@/types/common';

export const useQuantItemStore = defineStore('quantItem', () => {
  // 状态
  const items = ref<QuantItem[]>([]);
  const currentItem = ref<QuantItem | null>(null);
  const categories = ref<QuantItemCategory[]>([]);
  const currentCategory = ref<QuantItemCategory | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const pagination = ref({
    page: 1,
    pageSize: 10,
    total: 0
  });
  const filters = ref<QuantItemFilter>({});
  const sortBy = ref('');
  const sortOrder = ref('asc');

  // 计算属性
  const totalPages = computed(() => {
    return Math.ceil(pagination.value.total / pagination.value.pageSize);
  });

  const hasItems = computed(() => {
    return items.value.length > 0;
  });

  const hasCategories = computed(() => {
    return categories.value.length > 0;
  });

  const activeCategories = computed(() => {
    return categories.value.filter(c => c.is_active);
  });

  // 方法 - 量化项目
  async function fetchItems() {
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

      // 特殊处理is_active参数，确保正确转换为API期望的格式
      if (filters.value.is_active !== undefined && filters.value.is_active !== null) {
        console.log('处理is_active参数:', filters.value.is_active, typeof filters.value.is_active);
        
        // 正确处理字符串和布尔值
        if (filters.value.is_active === true || filters.value.is_active === '1') {
          params.is_active = '1';
        } else {
          params.is_active = '0';
        }
        
        console.log('转换后的is_active参数:', params.is_active);
      }
      
      console.log('最终参数:', params);
      const response = await getQuantItems(params);
      console.log('量化项目store接收到响应:', response);
      
      // 添加更多调试信息
      if (response?.data) {
        console.log('响应data属性类型:', typeof response.data);
        console.log('响应data属性键:', Object.keys(response.data));
      }
      
      // 更灵活地处理不同的响应格式
      if (response?.data?.data && Array.isArray(response.data.data)) {
        items.value = response.data.data;
        // 处理分页信息
        if (response.data.meta?.pagination) {
          pagination.value.total = response.data.meta.pagination.total || 0;
        } else {
          pagination.value.total = response.data.data.length;
        }
      } else if (response?.data && Array.isArray(response.data)) {
        items.value = response.data;
        pagination.value.total = response.data.length;
      } else if (Array.isArray(response)) {
        items.value = response;
        pagination.value.total = response.length;
      } else {
        console.error('未能解析的量化项目响应格式:', response);
        items.value = [];
        pagination.value.total = 0;
      }
      
      console.log('处理后的量化项目数据:', items.value);
      console.log('处理后的分页信息:', pagination.value);
    } catch (err) {
      console.error('获取量化项目列表失败:', err);
      error.value = '获取量化项目列表失败';
      items.value = [];
      pagination.value.total = 0;
    } finally {
      loading.value = false;
    }
  }

  async function fetchItemById(id: number) {
    loading.value = true;
    error.value = null;

    try {
      const response = await getQuantItem(id);
      currentItem.value = response.data.data;
      return response.data.data;
    } catch (err) {
      console.error(`Failed to fetch quant item with ID ${id}:`, err);
      error.value = '获取量化项目详情失败';
      return null;
    } finally {
      loading.value = false;
    }
  }

  async function addItem(itemData: CreateQuantItemPayload) {
    loading.value = true;
    error.value = null;

    try {
      const response = await createQuantItem(itemData);
      console.log('创建量化项目响应:', response);
      
      // 灵活处理不同的响应格式
      let newItem: QuantItem;
      
      if (response?.data?.data) {
        // 标准嵌套格式 response.data.data
        newItem = response.data.data;
      } else if (response?.data && typeof response.data === 'object' && 'id' in response.data) {
        // 直接对象格式 response.data
        newItem = response.data as unknown as QuantItem;
      } else if (response && typeof response === 'object' && 'id' in response) {
        // 直接返回对象
        newItem = response as unknown as QuantItem;
      } else {
        console.log('无法从响应中提取数据，尝试刷新列表获取最新数据');
        // 刷新列表，确保新添加的项目出现在列表中
        await fetchItems();
        return null;
      }
      
      // 刷新列表，确保新添加的项目出现在列表中
      await fetchItems();
      return newItem;
    } catch (err) {
      console.error('Failed to create quant item:', err);
      error.value = '创建量化项目失败';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function editItem(id: number, itemData: UpdateQuantItemPayload) {
    loading.value = true;
    error.value = null;

    try {
      const response = await updateQuantItem(id, itemData);
      console.log('编辑量化项目响应:', response);
      
      // 灵活处理不同的响应格式
      let updatedItem: QuantItem;
      
      if (response?.data?.data) {
        // 标准嵌套格式 response.data.data
        updatedItem = response.data.data;
      } else if (response?.data && typeof response.data === 'object' && 'id' in response.data) {
        // 直接对象格式 response.data
        updatedItem = response.data as unknown as QuantItem;
      } else if (response && typeof response === 'object' && 'id' in response) {
        // 直接返回对象
        updatedItem = response as unknown as QuantItem;
      } else {
        console.error('无法识别的响应格式:', response);
        throw new Error('返回数据格式异常');
      }
      
      // 更新当前项目（如果正在查看）
      if (currentItem.value && currentItem.value.id === id) {
        currentItem.value = updatedItem;
      }
      
      // 更新列表中的项目
      const index = items.value.findIndex(item => item.id === id);
      if (index !== -1) {
        items.value[index] = updatedItem;
      }
      
      return updatedItem;
    } catch (err) {
      console.error(`Failed to update quant item with ID ${id}:`, err);
      error.value = '更新量化项目失败';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function removeItem(id: number) {
    loading.value = true;
    error.value = null;

    try {
      await deleteQuantItem(id);
      
      // 如果删除的是当前正在查看的项目，清空当前项目
      if (currentItem.value && currentItem.value.id === id) {
        currentItem.value = null;
      }
      
      // 从列表中移除
      items.value = items.value.filter(item => item.id !== id);
      pagination.value.total -= 1;
      
      return true;
    } catch (err) {
      console.error(`Failed to delete quant item with ID ${id}:`, err);
      error.value = '删除量化项目失败';
      return false;
    } finally {
      loading.value = false;
    }
  }

  async function exportItems(params = {}) {
    loading.value = true;
    error.value = null;

    try {
      return await exportQuantItems({
        ...params,
        ...filters.value
      });
    } catch (err) {
      console.error('Failed to export quant items:', err);
      error.value = '导出量化项目失败';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function importItems(file: File) {
    loading.value = true;
    error.value = null;

    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await importQuantItems(formData);
      // 刷新列表
      await fetchItems();
      
      return response.data.data;
    } catch (err) {
      console.error('Failed to import quant items:', err);
      error.value = '导入量化项目失败';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  // 方法 - 量化项目分类
  async function fetchCategories() {
    loading.value = true;
    error.value = null;

    try {
      console.log('请求量化项目分类');
      const response = await getQuantItemCategories();
      console.log('量化项目分类store接收到响应:', response);
      
      // 添加更多调试信息
      if (response?.data) {
        console.log('分类响应data属性类型:', typeof response.data);
        console.log('分类响应data属性键:', Object.keys(response.data));
      }
      
      // 更灵活地处理不同的响应格式
      if (response?.data?.data && Array.isArray(response.data.data)) {
        categories.value = response.data.data;
      } else if (response?.data && Array.isArray(response.data)) {
        categories.value = response.data;
      } else if (Array.isArray(response)) {
        categories.value = response;
      } else {
        console.error('未能解析的量化项目分类响应格式:', response);
        // 使用本地默认分类作为回退
        const now = new Date().toISOString();
        categories.value = [
          { id: 1, name: '学习', description: '学习相关的量化项目', is_active: true, created_at: now, updated_at: now },
          { id: 2, name: '纪律', description: '纪律相关的量化项目', is_active: true, created_at: now, updated_at: now },
          { id: 3, name: '卫生', description: '卫生相关的量化项目', is_active: true, created_at: now, updated_at: now },
          { id: 4, name: '活动', description: '活动相关的量化项目', is_active: true, created_at: now, updated_at: now },
          { id: 5, name: '其他', description: '其他类型的量化项目', is_active: true, created_at: now, updated_at: now }
        ];
      }
      
      console.log('处理后的分类数据:', categories.value);
      return categories.value;
    } catch (err: any) {
      console.error('获取量化项目分类失败:', err);
      error.value = '获取量化项目分类失败';
      
      // 错误降级处理：如果API请求失败，提供本地默认分类
      if (err.response && err.response.status === 403) {
        console.log('使用本地默认分类作为回退');
        const now = new Date().toISOString();
        categories.value = [
          { id: 1, name: '学习', description: '学习相关的量化项目', is_active: true, created_at: now, updated_at: now },
          { id: 2, name: '纪律', description: '纪律相关的量化项目', is_active: true, created_at: now, updated_at: now },
          { id: 3, name: '卫生', description: '卫生相关的量化项目', is_active: true, created_at: now, updated_at: now },
          { id: 4, name: '活动', description: '活动相关的量化项目', is_active: true, created_at: now, updated_at: now },
          { id: 5, name: '其他', description: '其他类型的量化项目', is_active: true, created_at: now, updated_at: now }
        ];
        return categories.value;
      }
      
      categories.value = [];
      return [];
    } finally {
      loading.value = false;
    }
  }

  async function addCategory(categoryData: CreateQuantItemCategoryPayload) {
    loading.value = true;
    error.value = null;

    try {
      const response = await createQuantItemCategory(categoryData);
      console.log('创建分类响应:', response);
      
      // 灵活处理不同的响应格式
      let newCategory: QuantItemCategory;
      
      if (response?.data?.data) {
        // 标准嵌套格式 response.data.data
        newCategory = response.data.data;
      } else if (response?.data && typeof response.data === 'object' && 'id' in response.data) {
        // 直接对象格式 response.data
        newCategory = response.data as unknown as QuantItemCategory;
      } else if (response && typeof response === 'object' && 'id' in response) {
        // 直接返回对象
        newCategory = response as unknown as QuantItemCategory;
      } else {
        console.error('无法从响应中提取新创建的分类数据:', response);
        throw new Error('返回数据格式异常');
      }
      
      // 添加到列表
      categories.value.push(newCategory);
      
      return newCategory;
    } catch (err) {
      console.error('Failed to create category:', err);
      error.value = '创建量化项目分类失败';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function editCategory(id: number, categoryData: UpdateQuantItemCategoryPayload) {
    loading.value = true;
    error.value = null;

    try {
      const response = await updateQuantItemCategory(id, categoryData);
      console.log('分类更新响应:', response);
      
      // 灵活处理不同的响应格式
      let updatedCategory: QuantItemCategory;
      
      if (response?.data?.data) {
        // 标准嵌套格式 response.data.data
        updatedCategory = response.data.data;
      } else if (response?.data && typeof response.data === 'object' && 'id' in response.data) {
        // 直接对象格式 response.data
        updatedCategory = response.data as unknown as QuantItemCategory;
      } else if (response && typeof response === 'object' && 'id' in response) {
        // 直接返回对象
        updatedCategory = response as unknown as QuantItemCategory;
      } else {
        console.error('无法从响应中提取更新的分类数据:', response);
        throw new Error('返回数据格式异常');
      }
      
      // 更新当前分类（如果正在查看）
      if (currentCategory.value && currentCategory.value.id === id) {
        currentCategory.value = updatedCategory;
      }
      
      // 更新列表中的分类
      const index = categories.value.findIndex(category => category.id === id);
      if (index !== -1) {
        categories.value[index] = updatedCategory;
      }
      
      return updatedCategory;
    } catch (err) {
      console.error(`Failed to update category with ID ${id}:`, err);
      error.value = '更新量化项目分类失败';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function removeCategory(id: number) {
    loading.value = true;
    error.value = null;

    try {
      await deleteQuantItemCategory(id);
      
      // 如果删除的是当前正在查看的分类，清空当前分类
      if (currentCategory.value && currentCategory.value.id === id) {
        currentCategory.value = null;
      }
      
      // 从列表中移除
      categories.value = categories.value.filter(category => category.id !== id);
      
      return true;
    } catch (err) {
      console.error(`Failed to delete category with ID ${id}:`, err);
      error.value = '删除量化项目分类失败';
      return false;
    } finally {
      loading.value = false;
    }
  }

  // 分页和筛选方法
  function setPage(page: number) {
    pagination.value.page = page;
    fetchItems();
  }

  function setPageSize(size: number) {
    pagination.value.pageSize = size;
    pagination.value.page = 1; // 重置为第一页
    fetchItems();
  }

  function setFilters(newFilters: QuantItemFilter) {
    console.log('设置过滤条件:', JSON.stringify(newFilters));
    
    // 创建过滤器副本
    const processedFilters = { ...newFilters };
    
    // 特别记录 is_active 值用于调试
    if ('is_active' in processedFilters) {
      console.log('过滤条件中的 is_active:', processedFilters.is_active, typeof processedFilters.is_active);
    }
    
    // 不再额外处理is_active，保持原始布尔值
    
    filters.value = processedFilters;
    pagination.value.page = 1; // 重置为第一页
    fetchItems();
  }

  function setSorting(field: string, order: 'asc' | 'desc' = 'asc') {
    sortBy.value = field;
    sortOrder.value = order;
    fetchItems();
  }

  function reset() {
    items.value = [];
    currentItem.value = null;
    pagination.value = {
      page: 1,
      pageSize: 10,
      total: 0
    };
    filters.value = {};
    sortBy.value = '';
    sortOrder.value = 'asc';
    error.value = null;
  }

  return {
    // 状态
    items,
    currentItem,
    categories,
    currentCategory,
    loading,
    error,
    pagination,
    filters,
    sortBy,
    sortOrder,
    
    // 计算属性
    totalPages,
    hasItems,
    hasCategories,
    activeCategories,
    
    // 方法 - 量化项目
    fetchItems,
    fetchItemById,
    addItem,
    editItem,
    removeItem,
    exportItems,
    importItems,
    
    // 方法 - 量化项目分类
    fetchCategories,
    addCategory,
    editCategory,
    removeCategory,
    
    // 分页和筛选方法
    setPage,
    setPageSize,
    setFilters,
    setSorting,
    reset
  };
}); 