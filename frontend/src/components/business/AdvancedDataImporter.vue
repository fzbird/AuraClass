<template>
  <div class="advanced-data-importer">
    <n-card :title="title" size="small">
      <n-space vertical size="medium">
        <!-- 步骤导航 -->
        <n-steps :current="currentStep" size="small">
          <n-step title="选择文件" description="上传Excel或CSV文件" />
          <n-step title="数据验证" description="验证数据格式和内容" />
          <n-step title="确认导入" description="确认并导入数据" />
          <n-step title="完成" description="导入结果" />
        </n-steps>
        
        <div class="step-content">
          <!-- 步骤1: 选择文件 -->
          <div v-if="currentStep === 0" class="file-selection">
            <n-alert type="info" class="mb-4">
              <template #icon>
                <n-icon><info-circle-outlined /></n-icon>
              </template>
              <p>{{ fileSelectDescription || '请上传Excel文件(.xlsx, .xls)或CSV文件(.csv)。请确保数据符合模板格式。' }}</p>
            </n-alert>
            
            <n-space>
              <n-button @click="downloadTemplate">
                <template #icon>
                  <n-icon><download-outlined /></n-icon>
                </template>
                下载导入模板
              </n-button>
              
              <n-upload
                ref="uploadRef"
                :custom-request="handleImportUpload"
                :show-file-list="true"
                :max="1"
                :accept="acceptFileTypes"
              >
                <n-button type="primary">
                  <template #icon>
                    <n-icon><upload-outlined /></n-icon>
                  </template>
                  选择文件导入
                </n-button>
              </n-upload>
            </n-space>
            
            <n-divider />
            
            <n-space justify="end">
              <n-button 
                type="primary" 
                @click="goToStep(1)" 
                :disabled="!importFile"
              >
                下一步
              </n-button>
            </n-space>
          </div>
          
          <!-- 步骤2: 数据验证 -->
          <div v-else-if="currentStep === 1" class="validation-step">
            <div v-if="validating" class="validating-state">
              <n-spin size="large" />
              <p class="mt-4">正在验证数据，请稍候...</p>
            </div>
            
            <div v-else-if="validationResult">
              <n-alert 
                v-if="validationResult.success" 
                title="验证通过" 
                type="success"
                class="mb-4"
              >
                <template #icon>
                  <n-icon><check-circle-outlined /></n-icon>
                </template>
                <p>共 {{ validationResult.total }} 条数据验证通过，可以导入。</p>
              </n-alert>
              
              <n-alert 
                v-else 
                title="验证失败" 
                type="error"
                class="mb-4"
              >
                <template #icon>
                  <n-icon><close-circle-outlined /></n-icon>
                </template>
                <p>{{ validationResult.message }}</p>
              </n-alert>
              
              <!-- 预览数据表格 -->
              <div class="data-preview mb-4">
                <h3 class="text-base font-medium mb-2">数据预览</h3>
                <n-data-table
                  :columns="previewColumns"
                  :data="previewData"
                  :pagination="{ pageSize: 5 }"
                  :bordered="false"
                  :striped="true"
                />
              </div>
              
              <!-- 错误信息列表 -->
              <div v-if="validationResult.errors && validationResult.errors.length" class="validation-errors">
                <n-collapse>
                  <n-collapse-item title="错误详情" name="errors">
                    <n-list bordered>
                      <n-list-item v-for="(error, index) in validationResult.errors" :key="index">
                        <n-thing :title="`行 ${error.row} 错误`">
                          {{ error.message }}
                        </n-thing>
                      </n-list-item>
                    </n-list>
                  </n-collapse-item>
                </n-collapse>
              </div>
            </div>
            
            <n-divider />
            
            <n-space justify="space-between">
              <n-button @click="goToStep(0)">上一步</n-button>
              <n-button 
                type="primary" 
                @click="goToStep(2)"
                :disabled="!(validationResult && validationResult.success)"
              >
                下一步
              </n-button>
            </n-space>
          </div>
          
          <!-- 步骤3: 确认导入 -->
          <div v-else-if="currentStep === 2" class="confirm-step">
            <n-alert type="warning" class="mb-4">
              <template #icon>
                <n-icon><warning-outlined /></n-icon>
              </template>
              <p>请确认导入以下数据，此操作可能会修改或添加大量记录。</p>
            </n-alert>
            
            <n-descriptions bordered>
              <n-descriptions-item label="文件名">
                {{ importFile ? importFile.name : '-' }}
              </n-descriptions-item>
              <n-descriptions-item label="数据条数">
                {{ validationResult ? validationResult.total : 0 }}
              </n-descriptions-item>
              <n-descriptions-item label="数据类型">
                {{ dataTypeLabel }}
              </n-descriptions-item>
            </n-descriptions>
            
            <div class="import-options mt-4">
              <n-form ref="importOptionsForm" :model="importOptions" label-placement="left">
                <n-form-item label="导入选项" path="importMode">
                  <n-radio-group v-model:value="importOptions.importMode">
                    <n-space>
                      <n-radio value="add">仅添加新数据</n-radio>
                      <n-radio value="update">更新已有数据</n-radio>
                      <n-radio value="replace">替换已有数据</n-radio>
                    </n-space>
                  </n-radio-group>
                </n-form-item>
                
                <n-form-item label="冲突处理" path="conflictStrategy">
                  <n-radio-group v-model:value="importOptions.conflictStrategy">
                    <n-space>
                      <n-radio value="skip">跳过冲突数据</n-radio>
                      <n-radio value="override">覆盖已有数据</n-radio>
                    </n-space>
                  </n-radio-group>
                </n-form-item>
                
                <slot name="additionalOptions"></slot>
              </n-form>
            </div>
            
            <n-divider />
            
            <n-space justify="space-between">
              <n-button @click="goToStep(1)">上一步</n-button>
              <n-button 
                type="primary" 
                :loading="importing"
                @click="startImport"
              >
                开始导入
              </n-button>
            </n-space>
          </div>
          
          <!-- 步骤4: 完成 -->
          <div v-else-if="currentStep === 3" class="result-step">
            <div v-if="importing" class="importing-state">
              <n-spin size="large" />
              <p class="mt-4">正在导入数据，请稍候...</p>
              <n-progress 
                type="line" 
                :percentage="importProgress" 
                :indicator-placement="'inside'"
                :processing="importProgress < 100"
              />
              <p>{{ importProgressMessage }}</p>
            </div>
            
            <div v-else-if="importResult" class="import-result">
              <n-result
                :status="importResult.success ? 'success' : 'error'"
                :title="importResult.success ? '导入成功' : '导入失败'"
                :description="importResult.message"
              >
                <template #footer>
                  <n-space>
                    <n-button @click="resetImport">
                      返回
                    </n-button>
                    <n-button 
                      v-if="importResult.success"
                      type="primary"
                      @click="$emit('import-success', importResult)"
                    >
                      完成
                    </n-button>
                  </n-space>
                </template>
              </n-result>
              
              <!-- 导入详情 -->
              <div v-if="importResult.details" class="import-details mt-4">
                <n-collapse>
                  <n-collapse-item title="导入详情" name="details">
                    <n-descriptions bordered>
                      <n-descriptions-item v-for="(value, key) in importResult.details" 
                        :key="key" 
                        :label="getDetailLabel(key)"
                      >
                        {{ value }}
                      </n-descriptions-item>
                    </n-descriptions>
                  </n-collapse-item>
                </n-collapse>
              </div>
            </div>
          </div>
        </div>
      </n-space>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue';
import {
  NCard,
  NSpace,
  NButton,
  NUpload,
  NAlert,
  NIcon,
  NSpin,
  NSteps,
  NStep,
  NDivider,
  NDataTable,
  NDescriptions,
  NDescriptionsItem,
  NForm,
  NFormItem,
  NRadioGroup,
  NRadio,
  NCollapse,
  NCollapseItem,
  NList,
  NListItem,
  NThing,
  NProgress,
  NResult,
  useMessage
} from 'naive-ui';
import type { UploadCustomRequestOptions, UploadInst, DataTableColumns } from 'naive-ui';
import InfoCircleOutlined from '@vicons/antd/es/InfoCircleOutlined';
import DownloadOutlined from '@vicons/antd/es/DownloadOutlined';
import UploadOutlined from '@vicons/antd/es/UploadOutlined';
import CheckCircleOutlined from '@vicons/antd/es/CheckCircleOutlined';
import CloseCircleOutlined from '@vicons/antd/es/CloseCircleOutlined';
import WarningOutlined from '@vicons/antd/es/WarningOutlined';

interface ValidationError {
  row: number;
  column?: string;
  message: string;
}

interface ValidationResult {
  success: boolean;
  message?: string;
  total?: number;
  errors?: ValidationError[];
  data?: any[];
}

interface ImportResult {
  success: boolean;
  message: string;
  details?: Record<string, any>;
}

interface ImportOptions {
  importMode: 'add' | 'update' | 'replace';
  conflictStrategy: 'skip' | 'override';
  [key: string]: any;
}

const props = defineProps({
  title: {
    type: String,
    default: '高级数据导入'
  },
  apiEndpoint: {
    type: String,
    required: true
  },
  dataType: {
    type: String,
    required: true // 'students', 'records', 'quant-items', etc.
  },
  acceptFileTypes: {
    type: String,
    default: '.xlsx,.xls,.csv'
  },
  fileSelectDescription: {
    type: String,
    default: ''
  },
  defaultImportOptions: {
    type: Object,
    default: () => ({})
  }
});

const emit = defineEmits([
  'import-start',
  'import-progress',
  'import-success',
  'import-error',
  'validation-success',
  'validation-error',
  'reset'
]);

// 组件状态
const message = useMessage();
const currentStep = ref(0);
const uploadRef = ref<UploadInst | null>(null);
const importFile = ref<File | null>(null);
const validating = ref(false);
const importing = ref(false);
const validationResult = ref<ValidationResult | null>(null);
const importResult = ref<ImportResult | null>(null);
const previewData = ref<any[]>([]);
const previewColumns = ref<DataTableColumns>([]);
const importProgress = ref(0);
const importProgressMessage = ref('');

// 导入选项
const importOptions = reactive<ImportOptions>({
  importMode: 'add',
  conflictStrategy: 'skip',
  ...props.defaultImportOptions
});

// 计算属性：数据类型标签
const dataTypeLabel = computed(() => {
  const typeMap: Record<string, string> = {
    'students': '学生数据',
    'records': '量化记录',
    'quant-items': '量化项目',
    'classes': '班级数据'
  };
  
  return typeMap[props.dataType] || props.dataType;
});

// 下载导入模板
const downloadTemplate = async () => {
  try {
    // 根据数据类型下载对应的模板
    window.open(`/api/v1/${props.dataType}/template/download`, '_blank');
  } catch (error) {
    console.error('Template download failed:', error);
    message.error('下载模板失败');
  }
};

// 处理文件上传
const handleImportUpload = async ({ file }: UploadCustomRequestOptions) => {
  importFile.value = file.file;
  message.success(`文件 ${file.file?.name} 已选择`);
};

// 验证导入文件
const validateImportFile = async () => {
  if (!importFile.value) {
    message.warning('请先选择文件');
    return;
  }
  
  validating.value = true;
  validationResult.value = null;
  
  try {
    const formData = new FormData();
    formData.append('file', importFile.value);
    
    // 发送文件到验证API
    const response = await fetch(`/api/v1/${props.dataType}/validate-import`, {
      method: 'POST',
      body: formData,
    });
    
    const result = await response.json();
    
    if (result.success) {
      validationResult.value = {
        success: true,
        total: result.data.length,
        data: result.data
      };
      
      // 生成预览数据和列
      if (result.data.length > 0) {
        generatePreviewTable(result.data);
      }
      
      emit('validation-success', validationResult.value);
    } else {
      validationResult.value = {
        success: false,
        message: result.message || '数据验证失败',
        errors: result.errors || []
      };
      emit('validation-error', validationResult.value);
    }
  } catch (error) {
    console.error('Validation failed:', error);
    validationResult.value = {
      success: false,
      message: '验证过程中发生错误，请重试'
    };
    emit('validation-error', validationResult.value);
  } finally {
    validating.value = false;
  }
};

// 生成预览表格
const generatePreviewTable = (data: any[]) => {
  if (!data.length) return;
  
  // 获取第一条数据的所有字段作为列
  const firstItem = data[0];
  const columns: DataTableColumns = Object.keys(firstItem).map(key => ({
    title: key,
    key,
    // 对长文本进行截断
    ellipsis: {
      tooltip: true
    }
  }));
  
  previewColumns.value = columns;
  // 最多显示20条数据预览
  previewData.value = data.slice(0, 20);
};

// 开始导入
const startImport = async () => {
  if (!validationResult.value?.success) {
    message.warning('请先验证数据');
    return;
  }
  
  importing.value = true;
  importProgress.value = 0;
  importProgressMessage.value = '准备导入数据...';
  emit('import-start', importOptions);
  
  try {
    const formData = new FormData();
    formData.append('file', importFile.value!);
    
    // 添加导入选项
    Object.keys(importOptions).forEach(key => {
      formData.append(key, importOptions[key]);
    });
    
    // 设置模拟进度更新
    const interval = setInterval(() => {
      if (importProgress.value < 90) {
        importProgress.value += Math.random() * 10;
        importProgressMessage.value = `已处理 ${Math.round(importProgress.value)}%`;
      }
    }, 500);
    
    // 发送文件到导入API
    const response = await fetch(`/api/v1/${props.dataType}/import`, {
      method: 'POST',
      body: formData,
    });
    
    clearInterval(interval);
    importProgress.value = 100;
    importProgressMessage.value = '导入完成';
    
    const result = await response.json();
    
    if (result.success) {
      importResult.value = {
        success: true,
        message: result.message || '数据导入成功',
        details: result.details || {}
      };
      emit('import-success', importResult.value);
    } else {
      importResult.value = {
        success: false,
        message: result.message || '数据导入失败',
        details: result.details || {}
      };
      emit('import-error', importResult.value);
    }
  } catch (error) {
    console.error('Import failed:', error);
    importResult.value = {
      success: false,
      message: '导入过程中发生错误，请重试'
    };
    emit('import-error', importResult.value);
  } finally {
    importing.value = false;
  }
};

// 导航到指定步骤
const goToStep = (step: number) => {
  if (step === 1 && currentStep.value === 0) {
    // 从选择文件到验证步骤，需要先验证文件
    validateImportFile();
  }
  
  currentStep.value = step;
};

// 重置导入
const resetImport = () => {
  currentStep.value = 0;
  importFile.value = null;
  validationResult.value = null;
  importResult.value = null;
  previewData.value = [];
  previewColumns.value = [];
  importProgress.value = 0;
  importProgressMessage.value = '';
  
  // 重置表单
  Object.assign(importOptions, {
    importMode: 'add',
    conflictStrategy: 'skip',
    ...props.defaultImportOptions
  });
  
  if (uploadRef.value) {
    uploadRef.value.clear();
  }
  
  emit('reset');
};

// 获取详情标签
const getDetailLabel = (key: string): string => {
  const labelMap: Record<string, string> = {
    'created': '创建数量',
    'updated': '更新数量',
    'skipped': '跳过数量',
    'failed': '失败数量',
    'total': '总数量',
    'duration': '处理时间(秒)'
  };
  
  return labelMap[key] || key;
};
</script>

<style scoped>
.advanced-data-importer {
  max-width: 900px;
  margin: 0 auto;
}

.step-content {
  min-height: 300px;
  padding: 20px 0;
}

.validating-state,
.importing-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
}

.mb-4 {
  margin-bottom: 16px;
}

.mt-4 {
  margin-top: 16px;
}

.text-base {
  font-size: 14px;
}

.font-medium {
  font-weight: 500;
}
</style> 