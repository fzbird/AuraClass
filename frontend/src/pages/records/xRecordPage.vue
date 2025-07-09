<template>
  <div class="record-page">
    <page-header title="量化记录管理">
      <template #subtitle>
        管理学生量化记录，支持单条录入和批量录入
      </template>
      
      <template #actions>
        <n-space>
          <n-button type="primary" @click="showSingleForm = true">
            <template #icon>
              <n-icon><PlusOutlined /></n-icon>
            </template>
            添加记录
          </n-button>
          <n-button type="primary" ghost @click="showBatchForm = true">
            <template #icon>
              <n-icon><UserAddOutlined /></n-icon>
            </template>
            批量录入
          </n-button>
          <n-button type="primary" ghost @click="showTemplatePanel = true">
            <template #icon>
              <n-icon><SnippetsOutlined /></n-icon>
            </template>
            记录模板
          </n-button>
          <n-popover trigger="hover" placement="bottom">
            <template #trigger>
              <n-button quaternary circle>
                <template #icon>
                  <n-icon><DownOutlined /></n-icon>
                </template>
              </n-button>
            </template>
            <n-space vertical>
              <n-button @click="exportRecords">
                <template #icon>
                  <n-icon><DownloadOutlined /></n-icon>
                </template>
                导出记录
              </n-button>
              <n-button @click="showImportModal = true">
                <template #icon>
                  <n-icon><UploadOutlined /></n-icon>
                </template>
                导入记录
              </n-button>
            </n-space>
          </n-popover>
        </n-space>
      </template>
    </page-header>
    
    <!-- 过滤表单 -->
    <n-card class="mb-4">
      <n-form inline :model="filterModel" label-placement="left" label-width="auto">
        <n-grid :cols="24" :x-gap="24">
          <n-gi :span="6">
            <n-form-item label="班级">
              <n-select
                v-model:value="filterModel.class_id"
                filterable
                clearable
                placeholder="选择班级"
                :options="classOptions"
                @update:value="handleClassChange"
              />
            </n-form-item>
          </n-gi>
          
          <n-gi :span="6">
            <n-form-item label="学生">
              <n-select
                v-model:value="filterModel.student_id"
                filterable
                clearable
                placeholder="选择学生"
                :options="studentOptions"
                :loading="loadingStudents"
              />
            </n-form-item>
          </n-gi>
          
          <n-gi :span="6">
            <n-form-item label="量化项目">
              <n-select
                v-model:value="filterModel.item_id"
                filterable
                clearable
                placeholder="选择量化项目"
                :options="itemOptions"
                :loading="loadingItems"
              />
            </n-form-item>
          </n-gi>
          
          <n-gi :span="6">
            <n-form-item label="分数区间">
              <n-input-group>
                <n-input-number
                  v-model:value="filterModel.min_score"
                  placeholder="最小值"
                  style="width: 100px"
                />
                <n-input-number
                  v-model:value="filterModel.max_score"
                  placeholder="最大值"
                  style="width: 100px"
                />
              </n-input-group>
            </n-form-item>
          </n-gi>
          
          <n-gi :span="8">
            <n-form-item label="日期范围">
              <n-date-picker
                v-model:value="dateRange"
                type="daterange"
                clearable
                style="width: 100%"
              />
            </n-form-item>
          </n-gi>
          
          <n-gi :span="16">
            <n-space justify="end" style="width: 100%">
              <n-button @click="resetFilter">重置</n-button>
              <n-button type="primary" @click="applyFilter">应用筛选</n-button>
            </n-space>
          </n-gi>
        </n-grid>
      </n-form>
    </n-card>
    
    <!-- 记录表格 -->
    <n-card>
      <n-data-table
        ref="tableRef"
        :columns="columns"
        :data="records"
        :loading="loading"
        :pagination="pagination"
        :row-key="(row) => row.id"
        @update:page="handlePageChange"
        @update:page-size="handlePageSizeChange"
        @update:sorter="handleSorterChange"
      />
    </n-card>
    
    <!-- 记录表单弹窗 -->
    <n-modal
      v-model:show="showSingleForm"
      preset="card"
      title="添加量化记录"
      :style="{ width: '600px' }"
      :mask-closable="false"
    >
      <record-form
        ref="recordFormRef"
        :initial-values="formInitialValues"
        @submit="handleRecordSubmit"
        @cancel="showSingleForm = false"
      />
    </n-modal>
    
    <!-- 批量录入表单弹窗 -->
    <n-modal
      v-model:show="showBatchForm"
      preset="card"
      title="批量录入量化记录"
      :style="{ width: '800px' }"
      :mask-closable="false"
    >
      <record-batch-form
        @success="handleBatchFormSuccess"
        @cancel="showBatchForm = false"
      />
    </n-modal>

    <!-- 在已有内容后添加模板侧边面板 -->
    <n-drawer v-model:show="showTemplatePanel" display-directive="show" width="600">
      <n-drawer-content title="记录模板管理">
        <record-template 
          :user-id="currentUser.id" 
          @use-template="handleUseTemplate"
        />
      </n-drawer-content>
    </n-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, h, nextTick } from 'vue';
import { 
  NButton, 
  NSpace, 
  NCard, 
  NForm, 
  NFormItem, 
  NGrid, 
  NGi, 
  NSelect, 
  NInputNumber,
  NInputGroup, 
  NDatePicker, 
  NDataTable, 
  NModal, 
  NIcon,
  NBadge,
  NTag,
  NPopconfirm,
  useMessage,
  type DataTableColumns,
  type PaginationProps
} from 'naive-ui';
import PageHeader from '@/components/layout/PageHeader.vue';
import RecordForm from '@/components/business/RecordForm.vue';
import RecordBatchForm from '@/components/business/RecordBatchForm.vue';
import RecordTemplate from '@/components/business/RecordTemplate.vue';
import PlusOutlined from '@vicons/antd/es/PlusOutlined';
import DownloadOutlined from '@vicons/antd/es/DownloadOutlined';
import FolderAddOutlined from '@vicons/antd/es/FolderAddOutlined';
import EditOutlined from '@vicons/antd/es/EditOutlined';
import DeleteOutlined from '@vicons/antd/es/DeleteOutlined';
import UserAddOutlined from '@vicons/antd/es/UserAddOutlined';
import SnippetsOutlined from '@vicons/antd/es/SnippetsOutlined';
import DownOutlined from '@vicons/antd/es/DownOutlined';
import UploadOutlined from '@vicons/antd/es/UploadOutlined';
import { getClasses } from '@/services/api/classes';
import { getStudents } from '@/services/api/students';
import { getQuantItems } from '@/services/api/quant-items';
import { getQuantRecords, deleteQuantRecord, exportQuantRecords } from '@/services/api/records';
import { useUserStore } from '@/stores/user';
import type { SelectOption } from 'naive-ui';
import type { QuantRecord, QuantRecordFilter, RecordTemplate as RecordTemplateType } from '@/types/record';

const message = useMessage();

// 状态管理
const loading = ref(false);
const loadingStudents = ref(false);
const loadingItems = ref(false);
const showSingleForm = ref(false);
const showBatchForm = ref(false);
const showTemplatePanel = ref(false);
const currentRecord = ref<QuantRecord | null>(null);
const records = ref<QuantRecord[]>([]);
const dateRange = ref<[number, number] | null>(null);

// 表格和分页
const tableRef = ref(null);
const pagination = reactive<PaginationProps>({
  page: 1,
  pageSize: 10,
  showSizePicker: true,
  pageSizes: [10, 20, 50, 100],
  onChange: (page) => {
    pagination.page = page;
  },
  onUpdatePageSize: (pageSize) => {
    pagination.pageSize = pageSize;
    pagination.page = 1;
  }
});

// 排序和过滤状态
const sorter = ref({
  field: '',
  order: ''
});

// 选项数据
const classes = ref<{ id: number; name: string }[]>([]);
const students = ref<{ id: number; student_id_no: string; full_name: string }[]>([]);
const items = ref<{ id: number; name: string; category?: string }[]>([]);

// 过滤条件
const filterModel = reactive<QuantRecordFilter>({
  class_id: undefined,
  student_id: undefined,
  item_id: undefined,
  min_score: undefined,
  max_score: undefined,
  start_date: undefined,
  end_date: undefined
});

// 选项计算属性
const classOptions = computed<SelectOption[]>(() => 
  classes.value.map(cls => ({
    label: cls.name,
    value: cls.id
  }))
);

const studentOptions = computed<SelectOption[]>(() => 
  students.value.map(student => ({
    label: `${student.student_id_no} - ${student.full_name}`,
    value: student.id
  }))
);

const itemOptions = computed<SelectOption[]>(() => 
  items.value.map(item => ({
    label: `${item.name}${item.category ? ` - ${item.category}` : ''}`,
    value: item.id
  }))
);

// 表格列定义
const columns = computed<DataTableColumns>(() => [
  {
    title: 'ID',
    key: 'id',
    width: 80
  },
  {
    title: '学生',
    key: 'student_name',
    sorter: true
  },
  {
    title: '学号',
    key: 'student_id_no'
  },
  {
    title: '量化项目',
    key: 'item_name'
  },
  {
    title: '类别',
    key: 'category',
    render: (row) => row.category ? h(NTag, { type: 'info' }, { default: () => row.category }) : null
  },
  {
    title: '分数',
    key: 'score',
    sorter: true,
    render: (row) => {
      const type = row.score > 0 ? 'success' : (row.score < 0 ? 'error' : 'default');
      return h(NBadge, { value: row.score, type });
    }
  },
  {
    title: '原因',
    key: 'reason',
    ellipsis: {
      tooltip: true
    }
  },
  {
    title: '记录日期',
    key: 'record_date',
    sorter: true
  },
  {
    title: '操作',
    key: 'actions',
    width: 120,
    fixed: 'right',
    render: (row) => {
      return h(
        NSpace, 
        { align: 'center', justify: 'center' }, 
        {
          default: () => [
            h(
              NButton,
              {
                quaternary: true,
                type: 'info',
                size: 'small',
                onClick: () => editRecord(row)
              },
              {
                default: () => h(NIcon, null, { default: () => h(EditOutlined) })
              }
            ),
            h(
              NPopconfirm,
              {
                onPositiveClick: () => removeRecord(row)
              },
              {
                trigger: () => h(
                  NButton,
                  {
                    quaternary: true,
                    type: 'error',
                    size: 'small'
                  },
                  {
                    default: () => h(NIcon, null, { default: () => h(DeleteOutlined) })
                  }
                ),
                default: () => '确定删除此记录？'
              }
            )
          ]
        }
      );
    }
  }
]);

// 班级变更处理
const handleClassChange = (value: number | undefined) => {
  filterModel.class_id = value;
  filterModel.student_id = undefined;
  
  if (value) {
    loadStudentsByClass(value);
  } else {
    students.value = [];
  }
};

// 页码变更处理
const handlePageChange = (page: number) => {
  pagination.page = page;
  loadRecords();
};

// 每页条数变更处理
const handlePageSizeChange = (pageSize: number) => {
  pagination.pageSize = pageSize;
  pagination.page = 1;
  loadRecords();
};

// 排序变更处理
const handleSorterChange = (options: { columnKey: string, order: 'ascend' | 'descend' | false }) => {
  sorter.value.field = options.columnKey;
  sorter.value.order = options.order === 'ascend' ? 'asc' : (options.order === 'descend' ? 'desc' : '');
  loadRecords();
};

// 加载班级数据
const loadClasses = async () => {
  try {
    const response = await getClasses();
    if (response.data && response.data.data) {
      classes.value = response.data.data;
    }
  } catch (error) {
    console.error('Failed to load classes:', error);
    message.error('加载班级数据失败');
  }
};

// 加载班级学生数据
const loadStudentsByClass = async (classId: number) => {
  loadingStudents.value = true;
  try {
    const response = await getStudents({ class_id: classId, page_size: 1000 });
    if (response.data && response.data.data) {
      students.value = response.data.data;
    }
  } catch (error) {
    console.error('Failed to load students:', error);
    message.error('加载学生数据失败');
  } finally {
    loadingStudents.value = false;
  }
};

// 加载量化项目数据
const loadItems = async () => {
  loadingItems.value = true;
  try {
    const response = await getQuantItems();
    if (response.data && response.data.data) {
      items.value = response.data.data;
    }
  } catch (error) {
    console.error('Failed to load quant items:', error);
    message.error('加载量化项目失败');
  } finally {
    loadingItems.value = false;
  }
};

// 加载记录数据
const loadRecords = async () => {
  loading.value = true;
  
  try {
    // 构建请求参数
    const params: Record<string, any> = {
      page: pagination.page,
      page_size: pagination.pageSize
    };
    
    // 添加过滤条件
    if (filterModel.student_id) {
      params.student_id = filterModel.student_id;
    } else if (filterModel.class_id) {
      params.class_id = filterModel.class_id;
    }
    
    if (filterModel.item_id) {
      params.item_id = filterModel.item_id;
    }
    
    if (filterModel.min_score !== undefined) {
      params.min_score = filterModel.min_score;
    }
    
    if (filterModel.max_score !== undefined) {
      params.max_score = filterModel.max_score;
    }
    
    if (filterModel.start_date) {
      params.start_date = filterModel.start_date;
    }
    
    if (filterModel.end_date) {
      params.end_date = filterModel.end_date;
    }
    
    // 添加排序条件
    if (sorter.value.field && sorter.value.order) {
      params.sort_by = sorter.value.field;
      params.sort_order = sorter.value.order;
    }
    
    // 获取记录数据
    const response = await getQuantRecords(params);
    if (response.data) {
      records.value = response.data.data;
      pagination.itemCount = response.data.total;
    }
  } catch (error) {
    console.error('Failed to load records:', error);
    message.error('加载记录失败');
  } finally {
    loading.value = false;
  }
};

// 打开表单
const openForm = () => {
  currentRecord.value = null;
  showSingleForm.value = true;
};

// 编辑记录
const editRecord = (record: QuantRecord) => {
  currentRecord.value = record;
  showSingleForm.value = true;
};

// 打开批量表单
const openBatchForm = () => {
  showBatchForm.value = true;
};

// 删除记录
const removeRecord = async (record: QuantRecord) => {
  try {
    await deleteQuantRecord(record.id);
    message.success('记录删除成功');
    loadRecords();
  } catch (error) {
    console.error('Failed to delete record:', error);
    message.error('删除记录失败');
  }
};

// 表单提交成功处理
const handleFormSuccess = () => {
  showSingleForm.value = false;
  loadRecords();
};

// 批量表单提交成功处理
const handleBatchFormSuccess = () => {
  showBatchForm.value = false;
  loadRecords();
};

// 应用过滤
const applyFilter = () => {
  // 处理日期范围
  if (dateRange.value) {
    const [startDate, endDate] = dateRange.value;
    filterModel.start_date = new Date(startDate).toISOString().split('T')[0];
    filterModel.end_date = new Date(endDate).toISOString().split('T')[0];
  } else {
    filterModel.start_date = undefined;
    filterModel.end_date = undefined;
  }
  
  pagination.page = 1;
  loadRecords();
};

// 重置过滤
const resetFilter = () => {
  // 重置过滤条件
  filterModel.class_id = undefined;
  filterModel.student_id = undefined;
  filterModel.item_id = undefined;
  filterModel.min_score = undefined;
  filterModel.max_score = undefined;
  filterModel.start_date = undefined;
  filterModel.end_date = undefined;
  
  // 重置日期范围
  dateRange.value = null;
  
  // 重置分页和排序
  pagination.page = 1;
  sorter.value.field = '';
  sorter.value.order = '';
  
  // 重新加载数据
  loadRecords();
};

// 导出记录
const exportRecords = async () => {
  try {
    // 构建导出参数
    const params: Record<string, any> = {};
    
    if (filterModel.student_id) {
      params.student_id = filterModel.student_id;
    } else if (filterModel.class_id) {
      params.class_id = filterModel.class_id;
    }
    
    if (filterModel.item_id) {
      params.item_id = filterModel.item_id;
    }
    
    if (filterModel.min_score !== undefined) {
      params.min_score = filterModel.min_score;
    }
    
    if (filterModel.max_score !== undefined) {
      params.max_score = filterModel.max_score;
    }
    
    if (filterModel.start_date) {
      params.start_date = filterModel.start_date;
    }
    
    if (filterModel.end_date) {
      params.end_date = filterModel.end_date;
    }
    
    // 导出记录
    const response = await exportQuantRecords(params);
    
    // 处理下载文件
    const blob = new Blob([response as Blob], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `量化记录_${new Date().toISOString().split('T')[0]}.xlsx`;
    link.click();
    
    message.success('导出成功');
  } catch (error) {
    console.error('Failed to export records:', error);
    message.error('导出记录失败');
  }
};

// 获取当前用户
const userStore = useUserStore();
const currentUser = computed(() => userStore.user);

// 新增状态
const recordFormRef = ref(null);
const formInitialValues = ref(null);

// 处理使用模板事件
const handleUseTemplate = (template: RecordTemplateType) => {
  // 设置表单初始值
  formInitialValues.value = {
    item_id: template.item_id,
    score: template.score,
    reason: template.reason
  };
  
  // 关闭模板面板，打开记录表单
  showTemplatePanel.value = false;
  showSingleForm.value = true;
  
  // 等待表单组件挂载完成后重置表单
  nextTick(() => {
    if (recordFormRef.value) {
      recordFormRef.value.resetForm(formInitialValues.value);
    }
  });
};

// 组件挂载时初始化
onMounted(() => {
  loadClasses();
  loadItems();
  loadRecords();
});
</script>

<style scoped>
.mb-4 {
  margin-bottom: 16px;
}
</style> 