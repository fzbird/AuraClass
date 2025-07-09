import { defineStore } from 'pinia'
import { ref, computed, inject } from 'vue'
import type { QuantItem, QuantItemFilter, QuantItemCategory } from '@/types/quant-item'
import * as quantItemsApi from '@/services/api/quant-items'
import { useMessage } from 'naive-ui'

export const useQuantItemStore = defineStore('quantItems', () => {
  // 使用可选链和默认消息函数，防止在provider之外使用时出错
  const message = {
    success: (content: string) => {
      console.log('Success:', content);
    },
    error: (content: string) => {
      console.error('Error:', content);
    }
  };
  
  try {
    // 尝试获取message provider
    const naiveMessage = useMessage();
    if (naiveMessage) {
      message.success = naiveMessage.success;
      message.error = naiveMessage.error;
    }
  } catch (error) {
    console.warn('useMessage needs to be used in a component wrapped by n-message-provider');
  }
  
  const items = ref<QuantItem[]>([])
  const total = ref(0)
  const loading = ref(false)
  const categories = ref<QuantItemCategory[]>([])
  const currentFilter = ref<QuantItemFilter>({
    page: 1,
    pageSize: 10
  })

  const activeItems = computed(() => items.value.filter(item => item.isActive))
  
  async function fetchQuantItems(filter: QuantItemFilter = {}) {
    try {
      loading.value = true
      const mergedFilter = { ...currentFilter.value, ...filter }
      currentFilter.value = mergedFilter
      const { items: fetchedItems, total: totalCount } = await quantItemsApi.getQuantItems(mergedFilter)
      items.value = fetchedItems
      total.value = totalCount
    } catch (error) {
      message.error('获取量化项目列表失败')
      console.error('Failed to fetch quant items:', error)
    } finally {
      loading.value = false
    }
  }

  async function fetchCategories() {
    try {
      const fetchedCategories = await quantItemsApi.getQuantItemCategories()
      categories.value = fetchedCategories
    } catch (error) {
      message.error('获取量化项目分类失败')
      console.error('Failed to fetch categories:', error)
    }
  }

  async function createItem(data: Omit<QuantItem, 'id' | 'createdAt' | 'updatedAt'>) {
    try {
      const newItem = await quantItemsApi.createQuantItem(data)
      message.success('创建量化项目成功')
      await fetchQuantItems(currentFilter.value)
      return newItem
    } catch (error) {
      message.error('创建量化项目失败')
      console.error('Failed to create quant item:', error)
      throw error
    }
  }

  async function updateItem(id: number, data: Partial<QuantItem>) {
    try {
      const updatedItem = await quantItemsApi.updateQuantItem(id, data)
      message.success('更新量化项目成功')
      await fetchQuantItems(currentFilter.value)
      return updatedItem
    } catch (error) {
      message.error('更新量化项目失败')
      console.error('Failed to update quant item:', error)
      throw error
    }
  }

  async function deleteItem(id: number) {
    try {
      await quantItemsApi.deleteQuantItem(id)
      message.success('删除量化项目成功')
      await fetchQuantItems(currentFilter.value)
    } catch (error) {
      message.error('删除量化项目失败')
      console.error('Failed to delete quant item:', error)
      throw error
    }
  }

  async function toggleStatus(id: number, isActive: boolean) {
    try {
      await quantItemsApi.toggleQuantItemStatus(id, isActive)
      message.success(`${isActive ? '启用' : '禁用'}量化项目成功`)
      await fetchQuantItems(currentFilter.value)
    } catch (error) {
      message.error(`${isActive ? '启用' : '禁用'}量化项目失败`)
      console.error('Failed to toggle quant item status:', error)
      throw error
    }
  }

  return {
    items,
    total,
    loading,
    categories,
    currentFilter,
    activeItems,
    fetchQuantItems,
    fetchCategories,
    createItem,
    updateItem,
    deleteItem,
    toggleStatus
  }
}) 