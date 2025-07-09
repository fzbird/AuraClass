<template>
  <div class="batch-data-exporter">
    <n-card :title="title" size="small">
      <n-space vertical size="medium">
        <n-alert type="info">
          <template #icon>
            <n-icon><info-circle-outlined /></n-icon>
          </template>
          <p>{{ description || '选择合适的导出选项，支持Excel、CSV或PDF格式。' }}</p>
        </n-alert>
        
        <n-form
          ref="exportFormRef"
          :model="exportForm"
          label-placement="left"
          label-width="auto"
        >
          <!-- 基本选项 -->
          <n-grid :cols="24" :x-gap="16">
            <n-gi :span="12">
              <n-form-item label="导出格式" path="format" required>
                <n-select
                  v-model:value="exportForm.format"
                  :options="formatOptions"
                  placeholder="选择导出格式"
                />
              </n-form-item>
            </n-gi>
            
            <n-gi :span="12">
              <n-form-item label="数据范围" path="scope">
                <n-select
                  v-model:value="exportForm.scope"
                  :options="scopeOptions"
                  placeholder="选择数据范围"
                />
              </n-form-item>
            </n-gi>
            
            <n-gi :span="24">
              <n-form-item label="文件名称" path="filename">
                <n-input 
                  v-model:value="exportForm.filename"
                  placeholder="请输入导出文件名(不含扩展名)"
                />
              </n-form-item>
            </n-gi>
          </n-grid>
          
          <!-- 字段选择 -->
          <n-form-item label="导出字段" path="fields">
            <div class="field-selection mb-2">
              <n-space align="center">
                <n-checkbox v-model:checked="selectAllFields">全选</n-checkbox>
                <n-button text @click="resetFields">重置</n-button>
              </n-space>
            </div>
            
            <n-grid :cols="3" :x-gap="12" :y-gap="8">
              <n-gi v-for="field in availableFields" :key="field.value">
                <n-checkbox 
                  v-model:checked="exportForm.fields.includes(field.value)"
                  @update:checked="updateFieldSelection(field.value, $event)"
                >
                  {{ field.label }}
                </n-checkbox>
              </n-gi>
            </n-grid>
          </n-form-item>
          
          <!-- 格式特定选项 -->
          <div v-if="exportForm.format === 'pdf'">
            <n-form-item label="页面设置" path="pageSettings">
              <n-grid :cols="24" :x-gap="12">
                <n-gi :span="12">
                  <n-form-item label="纸张大小" path="pageSettings.format">
                    <n-select
                      v-model:value="exportForm.pageSettings.format"
                      :options="paperFormatOptions"
                      placeholder="选择纸张大小"
                    />
                  </n-form-item>
                </n-gi>
                
                <n-gi :span="12">
                  <n-form-item label="页面方向" path="pageSettings.orientation">
                    <n-radio-group v-model:value="exportForm.pageSettings.orientation">
                      <n-space>
                        <n-radio value="portrait">纵向</n-radio>
                        <n-radio value="landscape">横向</n-radio>
                      </n-space>
                    </n-radio-group>
                  </n-form-item>
                </n-gi>
              </n-grid>
            </n-form-item>
            
            <n-form-item label="显示选项" path="displayOptions">
              <n-space>
                <n-checkbox v-model:checked="exportForm.displayOptions.showTitle">
                  显示标题
                </n-checkbox>
                <n-checkbox v-model:checked="exportForm.displayOptions.showDate">
                  显示日期
                </n-checkbox>
                <n-checkbox v-model:checked="exportForm.displayOptions.showPageNum">
                  显示页码
                </n-checkbox>
              </n-space>
            </n-form-item>
          </div>
          
          <!-- 自定义筛选条件 -->
          <n-collapse v-if="showAdvancedOptions">
            <n-collapse-item title="高级筛选" name="advanced">
              <n-form-item label="日期范围" path="dateRange">
                <n-date-picker
                  v-model:value="exportForm.dateRange"
                  type="daterange"
                  clearable
                  style="width: 100%"
                />
              </n-form-item>
              
              <n-form-item v-if="hasCategories" label="分类" path="categories">
                <n-select
                  v-model:value="exportForm.categories"
                  :options="categoryOptions"
                  multiple
                  filterable
                  placeholder="选择分类"
                />
              </n-form-item>
              
              <n-form-item v-if="hasStatus" label="状态" path="status">
                <n-select
                  v-model:value="exportForm.status"
                  :options="statusOptions"
                  multiple
                  placeholder="选择状态"
                />
              </n-form-item>
              
              <slot name="customFilters"></slot>
            </n-collapse-item>
          </n-collapse>
          
          <!-- 操作按钮 -->
          <div class="actions-wrapper mt-4">
            <n-space justify="end">
              <n-button @click="resetForm">重置</n-button>
              <n-button 
                type="primary" 
                @click="startExport" 
                :loading="exporting"
                :disabled="!isFormValid"
              >
                <template #icon>
                  <n-icon><download-outlined /></n-icon>
                </template>
                开始导出
              </n-button>
            </n-space>
          </div>
        </n-form>
      </n-space>
      
      <!-- 导出进度弹窗 -->
      <n-modal
        v-model:show="showProgress"
        preset="card"
        title="导出进度"
        :mask-closable="false"
        style="width: 400px;"
      >
        <n-space vertical>
          <n-progress
            type="line"
            :percentage="exportProgress"
            :processing="exportProgress < 100"
            :indicator-placement="'inside'"
          />
          <p>{{ exportProgressMessage }}</p>
          
          <n-space justify="end" v-if="exportProgress === 100">
            <n-button @click="showProgress = false">关闭</n-button>
            <n-button v-if="exportResult?.downloadUrl" type="primary" @click="downloadExport">
              <template #icon>
                <n-icon><download-outlined /></n-icon>
              </template>
              下载文件
            </n-button>
          </n-space>
        </n-space>
      </n-modal>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue';
import {
  NCard,
  NForm,
  NFormItem,
  NInput,
  NSelect,
  NCheckbox,
  NRadioGroup,
  NRadio,
  NDatePicker,
  NButton,
  NSpace,
  NGrid,
  NGi,
  NIcon,
  NAlert,
  NCollapse,
  NCollapseItem,
  NProgress,
  NModal,
  useMessage
} from 'naive-ui';
import InfoCircleOutlined from '@vicons/antd/es/InfoCircleOutlined';
import DownloadOutlined from '@vicons/antd/es/DownloadOutlined';
import type { FormInst, SelectOption } from 'naive-ui';

interface ExportField {
  label: string;
  value: string;
}

interface ExportResult {
  success: boolean;
  message: string;
  downloadUrl?: string;
  filename?: string;
  totalRecords?: number;
}

const props = defineProps({
  title: {
    type: String,
    default: '数据导出'
  },
  description: {
    type: String,
    default: ''
  },
  apiEndpoint: {
    type: String,
    required: true
  },
  availableFields: {
    type: Array as () => ExportField[],
    required: true
  },
  defaultFields: {
    type: Array as () => string[],
    default: () => []
  },
  categoryOptions: {
    type: Array as () => SelectOption[],
    default: () => []
  },
  statusOptions: {
    type: Array as () => SelectOption[],
    default: () => []
  },
  scopeOptions: {
    type: Array as () => SelectOption[],
    default: () => [
      { label: '全部数据', value: 'all' },
      { label: '当前筛选', value: 'filtered' },
      { label: '当前选中', value: 'selected' }
    ]
  },
  selectedIds: {
    type: Array as () => (string | number)[],
    default: () => []
  },
  filters: {
    type: Object,
    default: () => ({})
  },
  showAdvancedOptions: {
    type: Boolean,
    default: true
  },
  hasCategories: {
    type: Boolean,
    default: false
  },
  hasStatus: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits([
  'export-start',
  'export-progress',
  'export-complete',
  'export-error'
]);

const message = useMessage();
const exportFormRef = ref<FormInst | null>(null);
const exporting = ref(false);
const showProgress = ref(false);
const exportProgress = ref(0);
const exportProgressMessage = ref('');
const exportResult = ref<ExportResult | null>(null);

// 导出表单
const exportForm = reactive({
  format: 'xlsx',
  scope: props.selectedIds.length > 0 ? 'selected' : 'all',
  filename: '',
  fields: props.defaultFields.length > 0 ? [...props.defaultFields] : props.availableFields.map(f => f.value),
  dateRange: null as [number, number] | null,
  categories: [] as (string | number)[],
  status: [] as string[],
  pageSettings: {
    format: 'a4',
    orientation: 'portrait'
  },
  displayOptions: {
    showTitle: true,
    showDate: true,
    showPageNum: true
  }
});

// 导出格式选项
const formatOptions = [
  { label: 'Excel文件 (.xlsx)', value: 'xlsx' },
  { label: 'CSV文件 (.csv)', value: 'csv' },
  { label: 'PDF文件 (.pdf)', value: 'pdf' }
];

// PDF纸张大小选项
const paperFormatOptions = [
  { label: 'A4', value: 'a4' },
  { label: 'A3', value: 'a3' },
  { label: 'Letter', value: 'letter' },
  { label: 'Legal', value: 'legal' }
];

// 计算属性：全选字段
const selectAllFields = computed({
  get: () => exportForm.fields.length === props.availableFields.length,
  set: (value) => {
    if (value) {
      exportForm.fields = props.availableFields.map(f => f.value);
    } else {
      exportForm.fields = [];
    }
  }
});

// 计算属性：表单是否有效
const isFormValid = computed(() => {
  return (
    exportForm.format && 
    exportForm.fields.length > 0 && 
    (exportForm.scope !== 'selected' || props.selectedIds.length > 0)
  );
});

// 监听已选择的ID变化
watch(() => props.selectedIds, (newIds) => {
  // 如果选中了新项，且范围是"选中"，检查选中项是否为空
  if (exportForm.scope === 'selected' && newIds.length === 0) {
    exportForm.scope = 'all';
    message.warning('没有选中的项目，已切换为"全部数据"');
  }
}, { deep: true });

// 更新字段选择
const updateFieldSelection = (field: string, checked: boolean) => {
  if (checked) {
    if (!exportForm.fields.includes(field)) {
      exportForm.fields.push(field);
    }
  } else {
    const index = exportForm.fields.indexOf(field);
    if (index !== -1) {
      exportForm.fields.splice(index, 1);
    }
  }
};

// 重置字段选择
const resetFields = () => {
  exportForm.fields = props.defaultFields.length > 0 
    ? [...props.defaultFields] 
    : props.availableFields.map(f => f.value);
};

// 重置表单
const resetForm = () => {
  exportForm.format = 'xlsx';
  exportForm.scope = props.selectedIds.length > 0 ? 'selected' : 'all';
  exportForm.filename = '';
  resetFields();
  exportForm.dateRange = null;
  exportForm.categories = [];
  exportForm.status = [];
  exportForm.pageSettings = {
    format: 'a4',
    orientation: 'portrait'
  };
  exportForm.displayOptions = {
    showTitle: true,
    showDate: true,
    showPageNum: true
  };
};

// 开始导出
const startExport = async () => {
  if (!isFormValid.value) {
    message.warning('请完善导出选项');
    return;
  }
  
  exporting.value = true;
  showProgress.value = true;
  exportProgress.value = 0;
  exportProgressMessage.value = '准备导出数据...';
  exportResult.value = null;
  
  // 通知父组件导出开始
  emit('export-start', {
    format: exportForm.format,
    scope: exportForm.scope,
    fields: exportForm.fields
  });
  
  try {
    // 构建请求数据
    const requestData = {
      format: exportForm.format,
      scope: exportForm.scope,
      filename: exportForm.filename,
      fields: exportForm.fields,
      selectedIds: exportForm.scope === 'selected' ? props.selectedIds : undefined,
      filters: {
        ...props.filters,
        dateRange: exportForm.dateRange,
        categories: exportForm.categories.length > 0 ? exportForm.categories : undefined,
        status: exportForm.status.length > 0 ? exportForm.status : undefined
      },
      options: {
        pageSettings: exportForm.format === 'pdf' ? exportForm.pageSettings : undefined,
        displayOptions: exportForm.format === 'pdf' ? exportForm.displayOptions : undefined
      }
    };
    
    // 模拟进度更新
    const progressInterval = setInterval(() => {
      if (exportProgress.value < 90) {
        exportProgress.value += Math.random() * 10;
        exportProgressMessage.value = `正在处理数据...(${Math.round(exportProgress.value)}%)`;
        
        // 通知父组件进度更新
        emit('export-progress', exportProgress.value);
      }
    }, 500);
    
    // 发送导出请求
    const response = await fetch(props.apiEndpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestData)
    });
    
    clearInterval(progressInterval);
    
    if (response.ok) {
      const result = await response.json();
      
      exportProgress.value = 100;
      exportProgressMessage.value = result.message || '导出完成';
      
      exportResult.value = {
        success: true,
        message: result.message || '导出成功',
        downloadUrl: result.downloadUrl,
        filename: result.filename,
        totalRecords: result.totalRecords
      };
      
      // 通知父组件导出完成
      emit('export-complete', exportResult.value);
      
      message.success('导出完成');
    } else {
      const errorData = await response.json();
      throw new Error(errorData.message || '导出失败');
    }
  } catch (error: any) {
    console.error('Export failed:', error);
    
    exportProgress.value = 100;
    exportProgressMessage.value = `导出失败: ${error.message}`;
    
    exportResult.value = {
      success: false,
      message: error.message || '导出过程中发生错误，请重试'
    };
    
    // 通知父组件导出错误
    emit('export-error', error);
    
    message.error('导出失败: ' + error.message);
  } finally {
    exporting.value = false;
  }
};

// 下载导出文件
const downloadExport = () => {
  if (exportResult.value?.downloadUrl) {
    window.open(exportResult.value.downloadUrl, '_blank');
  }
};
</script>

<style scoped>
.batch-data-exporter {
  max-width: 900px;
  margin: 0 auto;
}

.mb-2 {
  margin-bottom: 8px;
}

.mt-4 {
  margin-top: 16px;
}

.field-selection {
  border-bottom: 1px solid #f0f0f0;
  padding-bottom: 8px;
}
</style> 