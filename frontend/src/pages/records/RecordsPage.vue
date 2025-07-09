<template>
  <div class="records-page">
    <page-header title="量化记录管理">
      <template #actions>
        <n-space>
          <n-button type="primary" @click="showCreateModal = true">
            <template #icon>
              <n-icon>
                <PlusOutlined />
              </n-icon>
            </template>
            添加记录
          </n-button>
          <n-button @click="showImportModal = true">
            <template #icon>
              <n-icon>
                <UploadOutlined />
              </n-icon>
            </template>
            批量导入
          </n-button>
          <n-button @click="handleExport">
            <template #icon>
              <n-icon>
                <DownloadOutlined />
              </n-icon>
            </template>
            导出记录
          </n-button>
        </n-space>
      </template>
    </page-header>
    
    <!-- 过滤表单 -->
    <record-filter-form 
      @filter="handleFilter" 
      @reset="handleReset"
      class="mb-4" 
    />
    
    <!-- 数据表格 -->
    <n-card>
      <n-data-table
        :loading="loading"
        :columns="columns"
        :data="records"
        :pagination="pagination"
        :row-key="(row: QuantRecord) => row.id"
        @update:page="handlePageChange"
        @update:page-size="handlePageSizeChange"
        @update:sorter="handleSorterChange"
      />
    </n-card>
    
    <!-- 创建记录模态框 -->
    <n-modal
      v-model:show="showCreateModal"
      preset="dialog"
      title="添加量化记录"
      :style="{ width: '600px' }"
    >
      <template #default>
        <record-form v-if="showCreateModal" @success="handleCreateSuccess" @cancel="showCreateModal = false" />
      </template>
    </n-modal>
    
    <!-- 编辑记录模态框 -->
    <n-modal
      v-model:show="showEditModal"
      preset="dialog"
      title="编辑量化记录"
      :style="{ width: '600px' }"
    >
      <template #default>
        <record-form 
          v-if="showEditModal && currentRecord" 
          :record="currentRecord" 
          @success="handleEditSuccess" 
          @cancel="showEditModal = false" 
        />
      </template>
    </n-modal>
    
    <!-- 批量导入模态框 -->
    <n-modal
      v-model:show="showImportModal"
      preset="dialog"
      title="批量导入量化记录"
      :style="{ width: '80%', maxWidth: '1000px' }"
    >
      <template #default>
        <record-import-form v-if="showImportModal" @success="handleImportSuccess" />
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, h } from 'vue';
import { 
  NButton, 
  NSpace, 
  NCard, 
  NDataTable, 
  NModal, 
  NPopconfirm, 
  useMessage, 
  NIcon
} from 'naive-ui';
import type { DataTableColumns } from 'naive-ui';
import PageHeader from '@/components/layout/PageHeader.vue';
import RecordFilterForm from '@/components/business/RecordFilterForm.vue';
import RecordForm from '@/components/business/RecordForm.vue';
import RecordImportForm from '@/components/business/RecordImportForm.vue';
import PlusOutlined from '@vicons/antd/es/PlusOutlined';
import UploadOutlined from '@vicons/antd/es/UploadOutlined';
import DownloadOutlined from '@vicons/antd/es/DownloadOutlined';
import EditOutlined from '@vicons/antd/es/EditOutlined';
import DeleteOutlined from '@vicons/antd/es/DeleteOutlined';
import { getQuantRecords, deleteQuantRecord, exportQuantRecords } from '@/services/api/records';
import type { QuantRecord } from '@/types/record';

const message = useMessage();

// 表格数据
const records = ref<QuantRecord[]>([]);
const loading = ref(false);
const pagination = ref({
  page: 1,
  pageSize: 10,
  itemCount: 0,
  pageSizes: [10, 20, 50],
  showSizePicker: true,
});

// 过滤参数
const filterParams = ref<Record<string, any>>({});
const sortParams = ref<{
  sortBy?: string;
  sortOrder?: 'ascend' | 'descend' | false;
}>({});

// 模态框状态
const showCreateModal = ref(false);
const showEditModal = ref(false);
const showImportModal = ref(false);
const currentRecord = ref<QuantRecord | null>(null);

// 表格列定义
const columns = computed(() => [
  {
    title: '学生',
    key: 'student_name',
    sorter: true,
    sortOrder: sortParams.value.sortBy === 'student_name' ? sortParams.value.sortOrder : false,
  },
  {
    title: '量化项目',
    key: 'item_name',
    sorter: true,
    sortOrder: sortParams.value.sortBy === 'item_name' ? sortParams.value.sortOrder : false,
  },
  {
    title: '分数',
    key: 'score',
    sorter: true,
    sortOrder: sortParams.value.sortBy === 'score' ? sortParams.value.sortOrder : false,
    render(row: QuantRecord) {
      const score = Number(row.score);
      let colorClass = 'text-black';
      if (score > 0) colorClass = 'text-success';
      if (score < 0) colorClass = 'text-error';
      return h('span', { class: colorClass }, score);
    }
  },
  {
    title: '原因',
    key: 'reason',
    ellipsis: {
      tooltip: true,
    },
  },
  {
    title: '记录日期',
    key: 'record_date',
    sorter: true,
    sortOrder: sortParams.value.sortBy === 'record_date' ? sortParams.value.sortOrder : false,
  },
  {
    title: '操作',
    key: 'actions',
    fixed: 'right',
    width: 130,
    render(row: QuantRecord) {
      return h(NSpace, {}, {
        default: () => [
          h(
            NButton,
            {
              size: 'small',
              quaternary: true,
              type: 'info',
              onClick: () => handleEdit(row),
            },
            {
              default: () => h(NIcon, {}, { default: () => h(EditOutlined) }),
            }
          ),
          h(
            NPopconfirm,
            {
              onPositiveClick: () => handleDelete(row.id),
            },
            {
              default: () => '确认删除此记录吗？',
              trigger: () =>
                h(
                  NButton,
                  {
                    size: 'small',
                    quaternary: true,
                    type: 'error',
                  },
                  {
                    default: () => h(NIcon, {}, { default: () => h(DeleteOutlined) }),
                  }
                ),
            }
          ),
        ],
      });
    },
  },
]);

// 加载数据
const loadData = async () => {
  loading.value = true;
  try {
    const sortParamsObj = transformSortParams();
    console.log('排序参数对象:', sortParamsObj);
    
    const params = {
      page: pagination.value.page,
      page_size: pagination.value.pageSize,
      ...filterParams.value,
      ...sortParamsObj
    };
    
    console.log('请求参数:', params);
    const response = await getQuantRecords(params);
    
    // 添加调试输出
    console.log('量化记录响应:', response);
    
    // 直接使用响应作为记录数组
    if (Array.isArray(response)) {
      records.value = response;
      pagination.value.itemCount = response.length;
    } else if (response?.data && Array.isArray(response.data)) {
      records.value = response.data;
      pagination.value.itemCount = response.data.length;
    } else if (response?.items && Array.isArray(response.items)) {
      records.value = response.items;
      pagination.value.itemCount = response.total || response.items.length;
    } else {
      console.error('预期响应是数组，但收到了:', typeof response);
      records.value = [];
      pagination.value.itemCount = 0;
    }
  } catch (error) {
    console.error('Failed to load records:', error);
    message.error('加载量化记录失败');
    records.value = [];
    pagination.value.itemCount = 0;
  } finally {
    loading.value = false;
  }
};

// 转换排序参数格式
const transformSortParams = () => {
  if (!sortParams.value.sortBy || !sortParams.value.sortOrder) {
    return {};
  }
  
  // 使用类型断言确保返回值符合后端API期望的类型
  const sortOrder: 'asc' | 'desc' = sortParams.value.sortOrder === 'ascend' ? 'asc' : 'desc';
  
  // 返回后端API期望的排序参数格式
  return {
    sort_by: sortParams.value.sortBy,
    sort_order: sortOrder
  };
};

// 处理过滤
const handleFilter = (params: Record<string, any>) => {
  filterParams.value = params;
  pagination.value.page = 1;
  loadData();
};

// 重置过滤
const handleReset = () => {
  filterParams.value = {};
  pagination.value.page = 1;
  loadData();
};

// 处理分页变化
const handlePageChange = (page: number) => {
  pagination.value.page = page;
  loadData();
};

// 处理页大小变化
const handlePageSizeChange = (pageSize: number) => {
  pagination.value.pageSize = pageSize;
  pagination.value.page = 1;
  loadData();
};

// 处理排序变化
const handleSorterChange = (sorter: { columnKey: string, order: 'ascend' | 'descend' | false } | null) => {
  console.log('排序变化:', sorter);
  if (!sorter || !sorter.columnKey || !sorter.order) {
    sortParams.value = {};
  } else {
    sortParams.value = {
      sortBy: sorter.columnKey,
      sortOrder: sorter.order,
    };
  }
  console.log('排序参数:', sortParams.value);
  loadData();
};

// 处理编辑
const handleEdit = (record: any) => {
  currentRecord.value = record as QuantRecord;
  showEditModal.value = true;
};

// 处理删除
const handleDelete = async (id: number) => {
  try {
    await deleteQuantRecord(id);
    message.success('删除成功');
    loadData();
  } catch (error) {
    console.error('Failed to delete record:', error);
    message.error('删除失败');
  }
};

// 处理导出
const handleExport = async () => {
  try {
    const params = {
      ...filterParams.value,
    };
    
    const response = await exportQuantRecords(params);
    
    // 检查响应是否为Blob
    const blob = response instanceof Blob 
      ? response 
      : new Blob([response as any], { type: 'text/csv' });
    
    // 创建下载链接
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `量化记录_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
    
    message.success('导出成功');
  } catch (error) {
    console.error('Failed to export records:', error);
    message.error('导出失败');
  }
};

// 创建成功回调
const handleCreateSuccess = () => {
  showCreateModal.value = false;
  message.success('创建成功');
  loadData();
};

// 编辑成功回调
const handleEditSuccess = () => {
  showEditModal.value = false;
  message.success('更新成功');
  loadData();
};

// 导入成功回调
const handleImportSuccess = () => {
  message.success('导入成功');
  loadData();
};

// 初始加载
onMounted(() => {
  loadData();
});
</script>

<style scoped>
.text-success {
  color: var(--success-color);
}

.text-error {
  color: var(--error-color);
}

.mb-4 {
  margin-bottom: 16px;
}
</style>
