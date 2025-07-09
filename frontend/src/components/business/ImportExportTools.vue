<template>
  <div class="import-export-tools">
    <n-card :title="title" :bordered="false">
      <!-- 导入选项 -->
      <n-collapse v-if="showImport">
        <n-collapse-item title="导入数据" name="import">
          <n-space vertical :size="16">
            <n-alert title="导入说明" type="info">
              <template #icon>
                <n-icon><InfoCircleFilled /></n-icon>
              </template>
              <p>{{ importDescription || '请选择Excel文件(.xlsx)导入数据，确保数据符合模板格式。' }}</p>
            </n-alert>

            <n-space>
              <n-button @click="downloadTemplate">
                <template #icon>
                  <n-icon><DownloadOutlined /></n-icon>
                </template>
                下载导入模板
              </n-button>
              
              <n-upload
                ref="uploadRef"
                :custom-request="handleImportUpload"
                :show-file-list="false"
                :accept="acceptFileTypes"
              >
                <n-button type="primary">
                  <template #icon>
                    <n-icon><UploadOutlined /></n-icon>
                  </template>
                  选择文件导入
                </n-button>
              </n-upload>
            </n-space>

            <!-- 验证结果展示 -->
            <div v-if="validationResult">
              <n-alert v-if="validationResult.success" title="验证通过" type="success">
                <p>共 {{ validationResult.total }} 条数据，准备导入</p>
              </n-alert>
              <n-alert v-else title="验证失败" type="error">
                <p>{{ validationResult.message }}</p>
                <n-collapse v-if="validationResult.errors && validationResult.errors.length">
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
              </n-alert>
              
              <n-space justify="end" style="margin-top: 12px;">
                <n-button @click="resetImport">取消</n-button>
                <n-button 
                  type="primary" 
                  :disabled="!validationResult.success" 
                  :loading="importing"
                  @click="confirmImport"
                >
                  确认导入
                </n-button>
              </n-space>
            </div>
          </n-space>
        </n-collapse-item>
      </n-collapse>

      <!-- 导出选项 -->
      <n-collapse v-if="showExport">
        <n-collapse-item title="导出数据" name="export">
          <n-space vertical :size="16">
            <n-alert title="导出说明" type="info">
              <template #icon>
                <n-icon><InfoCircleFilled /></n-icon>
              </template>
              <p>{{ exportDescription || '选择合适的导出选项，可以导出为Excel、CSV或PDF格式。' }}</p>
            </n-alert>

            <n-form
              ref="exportFormRef"
              :model="exportForm"
              label-placement="left"
              label-width="auto"
            >
              <n-grid :cols="24" :x-gap="16">
                <n-gi :span="12">
                  <n-form-item label="导出格式" path="format">
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
                  <n-form-item label="包含字段" path="fields">
                    <n-checkbox-group v-model:value="exportForm.fields">
                      <n-space>
                        <n-checkbox 
                          v-for="field in availableFields" 
                          :key="field.value" 
                          :value="field.value"
                          :label="field.label"
                        />
                      </n-space>
                    </n-checkbox-group>
                  </n-form-item>
                </n-gi>
              </n-grid>
              
              <n-space justify="end">
                <n-button @click="resetExport">重置</n-button>
                <n-button type="primary" @click="handleExport" :loading="exporting">
                  <template #icon>
                    <n-icon><DownloadOutlined /></n-icon>
                  </template>
                  开始导出
                </n-button>
              </n-space>
            </n-form>
          </n-space>
        </n-collapse-item>
      </n-collapse>
    </n-card>

    <!-- 进度对话框 -->
    <n-modal
      v-model:show="showProgress"
      preset="card"
      title="处理进度"
      :mask-closable="false"
      style="width: 400px;"
    >
      <n-progress
        type="line"
        :percentage="progressPercentage"
        :processing="progressPercentage < 100"
        :indicator-placement="'inside'"
      />
      <p>{{ progressMessage }}</p>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';
import {
  NCard,
  NCollapse,
  NCollapseItem,
  NSpace,
  NButton,
  NIcon,
  NAlert,
  NUpload,
  NForm,
  NFormItem,
  NGrid,
  NGi,
  NSelect,
  NCheckboxGroup,
  NCheckbox,
  NModal,
  NProgress,
  NList,
  NListItem,
  NThing,
  useMessage
} from 'naive-ui';
import DownloadOutlined from '@vicons/antd/es/DownloadOutlined';
import UploadOutlined from '@vicons/antd/es/UploadOutlined';
import InfoCircleFilled from '@vicons/antd/es/InfoCircleFilled';
import type { UploadCustomRequestOptions } from 'naive-ui';
import type { UploadInst } from 'naive-ui';

interface ImportValidationResult {
  success: boolean;
  message?: string;
  total?: number;
  errors?: Array<{
    row: number;
    message: string;
  }>;
}

// 定义组件属性
const props = defineProps({
  title: {
    type: String,
    default: '导入/导出工具'
  },
  apiEndpoint: {
    type: String,
    required: true
  },
  showImport: {
    type: Boolean,
    default: true
  },
  showExport: {
    type: Boolean,
    default: true
  },
  importDescription: {
    type: String,
    default: ''
  },
  exportDescription: {
    type: String,
    default: ''
  },
  acceptFileTypes: {
    type: String,
    default: '.xlsx,.xls'
  },
  availableFields: {
    type: Array as () => Array<{ label: string; value: string }>,
    default: () => []
  },
  defaultFields: {
    type: Array as () => string[],
    default: () => []
  }
});

// 定义组件事件
const emit = defineEmits([
  'import-success',
  'import-error',
  'export-success',
  'export-error'
]);

// 组件状态
const message = useMessage();
const uploadRef = ref<UploadInst | null>(null);
const validationResult = ref<ImportValidationResult | null>(null);
const importing = ref(false);
const exporting = ref(false);
const showProgress = ref(false);
const progressPercentage = ref(0);
const progressMessage = ref('');
const importData = ref<any[] | null>(null);

// 导出表单
const exportForm = reactive({
  format: 'xlsx',
  scope: 'all',
  fields: props.defaultFields
});

// 导出格式选项
const formatOptions = [
  { label: 'Excel (.xlsx)', value: 'xlsx' },
  { label: 'CSV (.csv)', value: 'csv' },
  { label: 'PDF (.pdf)', value: 'pdf' }
];

// 数据范围选项
const scopeOptions = [
  { label: '全部数据', value: 'all' },
  { label: '当前筛选', value: 'filtered' },
  { label: '选中项', value: 'selected' }
];

// 下载导入模板
const downloadTemplate = async () => {
  try {
    const response = await fetch(`${props.apiEndpoint}/template`, {
      method: 'GET',
      headers: {
        'Accept': 'application/octet-stream'
      }
    });
    
    if (!response.ok) {
      throw new Error('下载模板失败');
    }
    
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = '导入模板.xlsx';
    link.click();
    URL.revokeObjectURL(url);
    
    message.success('模板下载成功');
  } catch (error) {
    console.error('下载模板失败:', error);
    message.error('下载模板失败');
  }
};

// 处理文件上传
const handleImportUpload = async (options: UploadCustomRequestOptions) => {
  const { file, onFinish } = options;
  if (!file) {
    message.error('请选择文件');
    return;
  }
  
  // 模拟进度
  showProgress.value = true;
  progressPercentage.value = 0;
  progressMessage.value = '正在上传文件...';
  
  const formData = new FormData();
  formData.append('file', file.file as File);
  
  try {
    // 上传并解析文件，显示模拟进度
    const progressInterval = setInterval(() => {
      if (progressPercentage.value < 90) {
        progressPercentage.value += 10;
      }
    }, 300);
    
    // 上传文件并验证
    const response = await fetch(`${props.apiEndpoint}/validate`, {
      method: 'POST',
      body: formData
    });
    
    clearInterval(progressInterval);
    progressPercentage.value = 100;
    showProgress.value = false;
    
    if (!response.ok) {
      throw new Error('文件上传失败');
    }
    
    const result = await response.json();
    validationResult.value = result;
    importData.value = result.data;
    
    onFinish();
  } catch (error) {
    console.error('文件上传失败:', error);
    message.error('文件上传失败');
    showProgress.value = false;
    onFinish();
  }
};

// 确认导入
const confirmImport = async () => {
  if (!validationResult.value?.success || !importData.value) {
    message.error('没有可导入的有效数据');
    return;
  }
  
  importing.value = true;
  showProgress.value = true;
  progressPercentage.value = 0;
  progressMessage.value = '正在导入数据...';
  
  try {
    // 模拟进度
    const totalItems = importData.value.length;
    const progressInterval = setInterval(() => {
      if (progressPercentage.value < 95) {
        progressPercentage.value += 5;
        progressMessage.value = `正在导入数据... (${Math.floor(progressPercentage.value * totalItems / 100)}/${totalItems})`;
      }
    }, 200);
    
    // 导入数据
    const response = await fetch(`${props.apiEndpoint}/import`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ data: importData.value })
    });
    
    clearInterval(progressInterval);
    progressPercentage.value = 100;
    progressMessage.value = '数据导入完成';
    
    if (!response.ok) {
      throw new Error('数据导入失败');
    }
    
    const result = await response.json();
    message.success(`成功导入 ${result.imported} 条数据`);
    emit('import-success', result);
    
    // 重置状态
    setTimeout(() => {
      showProgress.value = false;
      resetImport();
    }, 1000);
  } catch (error) {
    console.error('数据导入失败:', error);
    message.error('数据导入失败');
    emit('import-error', error);
    showProgress.value = false;
  } finally {
    importing.value = false;
  }
};

// 重置导入状态
const resetImport = () => {
  validationResult.value = null;
  importData.value = null;
  if (uploadRef.value) {
    uploadRef.value.clear();
  }
};

// 处理导出
const handleExport = async () => {
  exporting.value = true;
  showProgress.value = true;
  progressPercentage.value = 0;
  progressMessage.value = '正在准备导出数据...';
  
  try {
    // 模拟进度
    const progressInterval = setInterval(() => {
      if (progressPercentage.value < 90) {
        progressPercentage.value += 10;
        progressMessage.value = `正在生成${exportForm.format.toUpperCase()}文件...`;
      }
    }, 300);
    
    // 准备导出参数
    const params = new URLSearchParams({
      format: exportForm.format,
      scope: exportForm.scope,
      fields: exportForm.fields.join(',')
    });
    
    // 导出数据
    const response = await fetch(`${props.apiEndpoint}/export?${params.toString()}`, {
      method: 'GET',
    });
    
    clearInterval(progressInterval);
    progressPercentage.value = 100;
    progressMessage.value = '导出完成，准备下载...';
    
    if (!response.ok) {
      throw new Error('数据导出失败');
    }
    
    // 处理文件下载
    const contentType = response.headers.get('Content-Type') || '';
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    
    let filename = 'export';
    const contentDisposition = response.headers.get('Content-Disposition');
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
      if (filenameMatch && filenameMatch[1]) {
        filename = filenameMatch[1];
      }
    } else {
      filename = `export_${new Date().toISOString().split('T')[0]}.${exportForm.format}`;
    }
    
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
    
    message.success('数据导出成功');
    emit('export-success', { format: exportForm.format, filename });
    
    // 重置状态
    setTimeout(() => {
      showProgress.value = false;
    }, 1000);
  } catch (error) {
    console.error('数据导出失败:', error);
    message.error('数据导出失败');
    emit('export-error', error);
    showProgress.value = false;
  } finally {
    exporting.value = false;
  }
};

// 重置导出表单
const resetExport = () => {
  exportForm.format = 'xlsx';
  exportForm.scope = 'all';
  exportForm.fields = [...props.defaultFields];
};
</script>

<style scoped>
.import-export-tools {
  width: 100%;
}
</style> 