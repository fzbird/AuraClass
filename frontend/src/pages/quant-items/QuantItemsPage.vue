<template>
  <div class="p-6">
    <div class="mb-6">
      <div class="flex justify-between items-center mb-4">
        <h1 class="text-2xl font-bold">量化项目管理</h1>
        <n-space>
          <n-button @click="handleManageCategories">
            管理分类
          </n-button>
          <n-button type="primary" @click="handleCreate">
            新建量化项目
          </n-button>
        </n-space>
      </div>
      
      <n-card>
        <div class="flex gap-4 mb-4">
          <n-input
            v-model:value="filters.name"
            placeholder="搜索项目名称"
            @update:value="handleSearch"
          >
            <template #prefix>
              <n-icon>
                <search-icon />
              </n-icon>
            </template>
          </n-input>
          
          <n-select
            v-model:value="filters.category"
            :options="categoryOptions"
            placeholder="选择分类"
            clearable
            @update:value="handleCategoryChange"
          />
          
          <n-select
            v-model:value="filters.is_active"
            :options="statusOptions"
            placeholder="选择状态"
            clearable
            @update:value="handleStatusChange"
            value-field="value"
            label-field="label"
          />
        </div>
      </n-card>
    </div>

    <n-card>
      <n-data-table
        :columns="columns"
        :data="quantItemStore.items"
        :loading="quantItemStore.loading"
        :pagination="{
          page: quantItemStore.pagination.page,
          pageSize: quantItemStore.pagination.pageSize,
          itemCount: quantItemStore.pagination.total,
          onChange: handlePageChange,
          onUpdatePageSize: handlePageSizeChange,
          showSizePicker: true,
          pageSizes: [10, 20, 30, 50]
        }"
      />
    </n-card>

    <n-modal
      v-model:show="showFormModal"
      :mask-closable="false"
      preset="card"
      :title="modalTitle"
      :style="{ width: '700px' }"
    >
      <quant-item-form
        :initial-data="selectedItem"
        :loading="formLoading"
        @submit="handleFormSubmit"
        @cancel="showFormModal = false"
      />
    </n-modal>

    <n-modal
      v-model:show="showCategoryModal"
      :mask-closable="false"
      :auto-focus="false"
      preset="card"
      title="分类管理"
      :style="{ width: '500px', zIndex: 1000 }"
      transform-origin="center"
    >
      <template #default>
        <category-management 
          :categories="quantItemStore.categories"
          :loading="quantItemStore.loading"
          @add="handleCategoryAdd"
          @edit="handleCategoryEdit"
          @delete="handleCategoryDelete"
          @cancel="showCategoryModal = false"
        />
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, h } from 'vue'
import { 
  NButton, 
  NSpace, 
  NTag, 
  useDialog, 
  useMessage, 
  NIcon 
} from 'naive-ui'
import { useQuantItemStore } from '@/stores/quant-item'
import type { 
  QuantItem, 
  CreateQuantItemPayload, 
  UpdateQuantItemPayload, 
  QuantItemCategory, 
  CreateQuantItemCategoryPayload, 
  UpdateQuantItemCategoryPayload, 
  QuantItemFilter 
} from '@/types/quant-item'
import QuantItemForm from '@/components/business/quant-items/QuantItemForm.vue'
import CategoryManagement from '@/components/business/quant-items/CategoryManagement.vue'

// 自定义图标组件
const SearchIcon = () => h(
  'svg',
  {
    viewBox: '0 0 24 24',
    width: '1em',
    height: '1em',
    fill: 'none',
    stroke: 'currentColor',
    strokeWidth: 2,
    strokeLinecap: 'round',
    strokeLinejoin: 'round'
  },
  [
    h('circle', { cx: 11, cy: 11, r: 8 }),
    h('line', { x1: 21, y1: 21, x2: 16.65, y2: 16.65 })
  ]
)

const quantItemStore = useQuantItemStore()
const dialog = useDialog()
const message = useMessage()

const filters = ref<QuantItemFilter>({})
const showFormModal = ref(false)
const showCategoryModal = ref(false)
const selectedItem = ref<Partial<QuantItem> | undefined>(undefined)
const formLoading = ref(false)
const sortInfo = ref({
  field: '',
  order: ''
})
const loading = ref(false)
const formRef = ref<InstanceType<typeof QuantItemForm> | null>(null)

const modalTitle = computed(() => 
  selectedItem.value?.id ? '编辑量化项目' : '新建量化项目'
)

const categoryOptions = computed(() => 
  quantItemStore.categories.map((category: QuantItemCategory) => ({
    label: category.name,
    value: category.name
  }))
)

const statusOptions = [
  { label: '启用', value: '1' },
  { label: '禁用', value: '0' }
]

const pagination = computed(() => ({
  page: quantItemStore.pagination.page,
  pageSize: quantItemStore.pagination.pageSize,
  itemCount: quantItemStore.pagination.total,
  showSizePicker: true,
  pageSizes: [10, 20, 50],
  prefix: ({ itemCount }: { itemCount: number }) => `共 ${itemCount} 条`
}))

interface CategoryObject {
  id: number;
  name: string;
  [key: string]: any;
}

const formatCategory = (category: any): string => {
  if (!category) return '-'
  if (typeof category === 'string') return category
  if (typeof category === 'object' && 'name' in category) {
    return category.name as string
  }
  return '-'
}

const columns = [
  {
    title: '项目名称',
    key: 'name',
    width: 200,
    sorter: true
  },
  {
    title: '分类',
    key: 'category',
    width: 120,
    render: (row: QuantItem) => formatCategory(row.category)
  },
  {
    title: '描述',
    key: 'description',
    ellipsis: {
      tooltip: true
    }
  },
  {
    title: '分值范围',
    key: 'scoreRange',
    width: 120,
    render: (row: QuantItem) => `${row.min_score} ~ ${row.max_score}`
  },
  {
    title: '默认分值',
    key: 'default_score',
    width: 100,
    render: (row: QuantItem) => {
      const scoreValue = row.default_score;
      // 处理undefined、null和NaN的情况
      if (scoreValue === undefined || scoreValue === null) {
        return '-';
      }
      
      // 处理字符串和数字类型
      const score = typeof scoreValue === 'string' 
        ? parseFloat(scoreValue) 
        : scoreValue;
        
      // 确保是有效数字
      return isNaN(score) ? '-' : score.toFixed(1);
    }
  },
  {
    title: '权重',
    key: 'weight',
    width: 80
  },
  {
    title: '状态',
    key: 'is_active',
    width: 100,
    render: (row: QuantItem) => h(
      NTag,
      { type: row.is_active ? 'success' : 'error' },
      { default: () => row.is_active ? '启用' : '禁用' }
    )
  },
  {
    title: '操作',
    key: 'actions',
    width: 200,
    fixed: 'right',
    render: (row: QuantItem) => h(
      NSpace,
      { align: 'center' },
      {
        default: () => [
          h(
            NButton,
            {
              size: 'small',
              onClick: () => handleEdit(row)
            },
            { default: () => '编辑' }
          ),
          h(
            NButton,
            {
              size: 'small',
              type: row.is_active ? 'warning' : 'success',
              onClick: () => handleToggleStatus(row)
            },
            { default: () => row.is_active ? '禁用' : '启用' }
          ),
          h(
            NButton,
            {
              size: 'small',
              type: 'error',
              onClick: () => handleDelete(row)
            },
            { default: () => '删除' }
          )
        ]
      }
    )
  }
]

onMounted(async () => {
  console.log('QuantItemsPage挂载');
  loading.value = true;
  try {
    console.log('开始加载量化项目数据');
    await Promise.all([
      quantItemStore.fetchItems(),
      quantItemStore.fetchCategories()
    ]);
    console.log(
      `数据加载完成: ${quantItemStore.items.length} 个项目, ${quantItemStore.categories.length} 个分类`
    );
  } catch (error) {
    console.error('加载量化项目数据失败:', error);
    message.error('加载数据失败，请刷新页面重试');
  } finally {
    loading.value = false;
  }
});

const handleSearch = () => {
  quantItemStore.setFilters(filters.value)
}

const handleCategoryChange = () => {
  quantItemStore.setFilters(filters.value)
}

const handleStatusChange = (value: string | null) => {
  console.log('状态过滤值变更:', value, typeof value);
  
  // 值为null时表示清除筛选
  if (value === null) {
    // 删除筛选条件
    delete filters.value.is_active;
  } else {
    // 直接保存字符串值，不转换为布尔值
    filters.value.is_active = value; // 保持字符串值 '0' 或 '1'
  }
  
  console.log('更新后的过滤器:', JSON.stringify(filters.value));
  quantItemStore.setFilters(filters.value);
};

const handlePageChange = (page: number) => {
  quantItemStore.setPage(page)
}

const handlePageSizeChange = (pageSize: number) => {
  quantItemStore.setPageSize(pageSize)
}

const handleSorterChange = (sorter: { columnKey: string, order: 'ascend' | 'descend' | false }) => {
  if (!sorter || !sorter.columnKey || !sorter.order) {
    sortInfo.value = { field: '', order: '' }
    quantItemStore.setSorting('', 'asc')
    return
  }

  const field = sorter.columnKey as string
  const order = sorter.order === 'ascend' ? 'asc' : 'desc'
  
  sortInfo.value = { field, order }
  quantItemStore.setSorting(field, order)
}

const handleCreate = () => {
  selectedItem.value = undefined
  showFormModal.value = true
}

const handleEdit = (item: QuantItem) => {
  // Convert string numeric values to actual numbers
  const processedItem = { ...item };
  
  // Check if numeric fields are strings and convert them
  if (typeof processedItem.default_score === 'string') {
    processedItem.default_score = Number(processedItem.default_score);
  }
  
  if (typeof processedItem.min_score === 'string') {
    processedItem.min_score = Number(processedItem.min_score);
  }
  
  if (typeof processedItem.max_score === 'string') {
    processedItem.max_score = Number(processedItem.max_score);
  }
  
  if (typeof processedItem.weight === 'string') {
    processedItem.weight = Number(processedItem.weight);
  }
  
  console.log('Processing item for edit:', {
    original: item,
    processed: processedItem
  });
  
  selectedItem.value = processedItem;
  showFormModal.value = true;
}

const handleFormSubmit = async (data: CreateQuantItemPayload | UpdateQuantItemPayload) => {
  try {
    formLoading.value = true
    
    // Process data to ensure numeric values are actually numbers
    const processedData = {
      ...data,
      default_score: typeof data.default_score === 'string' ? Number(data.default_score) : data.default_score,
      min_score: typeof data.min_score === 'string' ? Number(data.min_score) : data.min_score,
      max_score: typeof data.max_score === 'string' ? Number(data.max_score) : data.max_score,
      weight: typeof data.weight === 'string' ? Number(data.weight) : data.weight
    };
    
    // Validate numeric values
    if (
      isNaN(Number(processedData.default_score)) || 
      isNaN(Number(processedData.min_score)) || 
      isNaN(Number(processedData.max_score)) || 
      isNaN(Number(processedData.weight))
    ) {
      throw new Error('Invalid numeric values in form data');
    }
    
    console.log('Submitting processed data:', processedData);
    
    if (selectedItem.value?.id) {
      await quantItemStore.editItem(selectedItem.value.id, processedData as UpdateQuantItemPayload)
      message.success('更新量化项目成功')
    } else {
      await quantItemStore.addItem(processedData as CreateQuantItemPayload)
      message.success('创建量化项目成功')
    }
    showFormModal.value = false
  } catch (error) {
    console.error('Failed to save quant item:', error)
    message.error(selectedItem.value?.id ? '更新量化项目失败' : '创建量化项目失败')
  } finally {
    formLoading.value = false
  }
}

const handleToggleStatus = async (item: QuantItem) => {
  try {
    const newStatus = !item.is_active;
    console.log(`尝试${newStatus ? '启用' : '禁用'}量化项目:`, item.id);
    
    // 仅发送状态变更参数
    const updateData: UpdateQuantItemPayload = { is_active: newStatus };
    const updatedItem = await quantItemStore.editItem(item.id, updateData);
    
    console.log('状态更新成功:', updatedItem);
    message.success(`${newStatus ? '启用' : '禁用'}量化项目成功`);
  } catch (error) {
    console.error('Failed to toggle quant item status:', error);
    message.error(`${!item.is_active ? '启用' : '禁用'}量化项目失败`);
  }
};

const handleDelete = (item: QuantItem) => {
  dialog.warning({
    title: '删除确认',
    content: `确定要删除量化项目"${item.name}"吗？此操作不可撤销。`,
    positiveText: '确定删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await quantItemStore.removeItem(item.id)
        message.success('删除量化项目成功')
      } catch (error) {
        console.error('Failed to delete quant item:', error)
        message.error('删除量化项目失败')
      }
    }
  })
}

const handleManageCategories = () => {
  console.log('打开分类管理模态框');
  showCategoryModal.value = true;
}

const handleCategoryAdd = async (data: CreateQuantItemCategoryPayload) => {
  try {
    await quantItemStore.addCategory(data)
    message.success('创建分类成功')
  } catch (error) {
    console.error('Failed to create category:', error)
    message.error('创建分类失败')
  }
}

const handleCategoryEdit = async (id: number, data: UpdateQuantItemCategoryPayload) => {
  try {
    await quantItemStore.editCategory(id, data)
    message.success('更新分类成功')
  } catch (error) {
    console.error('Failed to update category:', error)
    message.error('更新分类失败')
  }
}

const handleCategoryDelete = async (id: number) => {
  dialog.warning({
    title: '删除确认',
    content: '确定要删除此分类吗？此操作不可撤销，相关的量化项目将会失去分类关联。',
    positiveText: '确定删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await quantItemStore.removeCategory(id)
        message.success('删除分类成功')
      } catch (error) {
        console.error('Failed to delete category:', error)
        message.error('删除分类失败')
      }
    }
  })
}
</script>
