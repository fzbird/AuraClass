<template>
  <div class="batch-operation-panel">
    <n-card :title="title" :bordered="false">
      <template #header-extra>
        <n-button v-if="isOpen" @click="closeBatchOperation" size="small">
          <template #icon>
            <n-icon><CloseOutlined /></n-icon>
          </template>
          取消批量操作
        </n-button>
        <n-button v-else @click="openBatchOperation" size="small" type="primary">
          <template #icon>
            <n-icon><CheckSquareOutlined /></n-icon>
          </template>
          开始批量操作
        </n-button>
      </template>
      
      <div v-if="isOpen" class="batch-content">
        <n-alert v-if="selectedItems.length === 0" type="warning">
          <template #icon>
            <n-icon><InfoCircleOutlined /></n-icon>
          </template>
          请先选择要操作的项目
        </n-alert>
        
        <div v-else class="selected-summary">
          <div class="selected-info">
            <n-tag type="info" size="medium">已选择 {{ selectedItems.length }} 项</n-tag>
            <n-button text @click="emit('clear-selection')">清空选择</n-button>
          </div>
          
          <n-divider />
          
          <div class="operation-options">
            <n-space vertical>
              <n-form
                ref="batchFormRef"
                :model="batchForm"
                label-placement="left"
                label-width="auto"
              >
                <!-- 批量操作类型选择 -->
                <n-form-item label="操作类型" path="operation">
                  <n-select
                    v-model:value="batchForm.operation"
                    :options="operationOptions"
                    @update:value="handleOperationChange"
                  />
                </n-form-item>
                
                <!-- 按操作类型显示不同的表单控件 -->
                <template v-if="batchForm.operation === 'edit'">
                  <n-form-item v-if="batchEditFields.includes('class_id')" label="修改班级" path="class_id">
                    <n-select
                      v-model:value="batchForm.class_id"
                      filterable
                      placeholder="选择班级"
                      :options="classOptions"
                      clearable
                    />
                  </n-form-item>
                  
                  <n-form-item v-if="batchEditFields.includes('category')" label="修改分类" path="category">
                    <n-select
                      v-model:value="batchForm.category"
                      filterable
                      placeholder="选择分类"
                      :options="categoryOptions"
                      clearable
                    />
                  </n-form-item>
                  
                  <n-form-item v-if="batchEditFields.includes('status')" label="修改状态" path="status">
                    <n-select
                      v-model:value="batchForm.status"
                      placeholder="选择状态"
                      :options="statusOptions"
                      clearable
                    />
                  </n-form-item>
                  
                  <n-form-item v-if="batchEditFields.includes('tags')" label="添加标签" path="tags">
                    <n-select
                      v-model:value="batchForm.tags"
                      multiple
                      filterable
                      tag
                      placeholder="添加标签"
                      :options="tagOptions"
                    />
                  </n-form-item>
                </template>
                
                <template v-else-if="batchForm.operation === 'delete'">
                  <n-alert type="error">
                    <template #icon>
                      <n-icon><WarningOutlined /></n-icon>
                    </template>
                    将要删除 {{ selectedItems.length }} 项数据，此操作不可撤销！
                  </n-alert>
                  <n-form-item label="确认删除" path="confirmDelete">
                    <n-checkbox v-model:checked="batchForm.confirmDelete">
                      我已了解此操作的风险，确认删除所选项目
                    </n-checkbox>
                  </n-form-item>
                </template>
                
                <template v-else-if="batchForm.operation === 'export'">
                  <n-form-item label="导出格式" path="exportFormat">
                    <n-radio-group v-model:value="batchForm.exportFormat">
                      <n-space>
                        <n-radio value="xlsx">Excel (.xlsx)</n-radio>
                        <n-radio value="csv">CSV (.csv)</n-radio>
                        <n-radio value="pdf">PDF (.pdf)</n-radio>
                      </n-space>
                    </n-radio-group>
                  </n-form-item>
                </template>
                
                <template v-else-if="batchForm.operation === 'custom'">
                  <slot name="customBatchFields"></slot>
                </template>
              </n-form>
              
              <n-space justify="end">
                <n-button @click="closeBatchOperation">取消</n-button>
                <n-button 
                  type="primary"
                  :disabled="!isValid"
                  :loading="loading"
                  @click="handleApplyBatch"
                >
                  应用操作
                </n-button>
              </n-space>
            </n-space>
          </div>
        </div>
      </div>
      
      <div v-else class="batch-placeholder">
        <p>{{ placeholder || '开启批量操作模式后，可以同时对多个项目进行编辑、删除或导出等操作' }}</p>
      </div>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue';
import {
  NCard,
  NButton,
  NIcon,
  NAlert,
  NSpace,
  NForm,
  NFormItem,
  NSelect,
  NCheckbox,
  NRadioGroup,
  NRadio,
  NDivider,
  NTag,
  useMessage
} from 'naive-ui';
import type { FormInst, SelectOption } from 'naive-ui';
import CloseOutlined from '@vicons/antd/es/CloseOutlined';
import CheckSquareOutlined from '@vicons/antd/es/CheckSquareOutlined';
import InfoCircleOutlined from '@vicons/antd/es/InfoCircleOutlined';
import WarningOutlined from '@vicons/antd/es/WarningOutlined';

// 定义组件属性
const props = defineProps({
  title: {
    type: String,
    default: '批量操作'
  },
  placeholder: {
    type: String,
    default: ''
  },
  selectedItems: {
    type: Array as () => any[],
    default: () => []
  },
  batchEditFields: {
    type: Array as () => string[],
    default: () => ['class_id', 'status', 'tags']
  },
  classOptions: {
    type: Array as () => SelectOption[],
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
  tagOptions: {
    type: Array as () => SelectOption[],
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
});

// 定义事件
const emit = defineEmits([
  'open',
  'close',
  'clear-selection',
  'apply-batch',
  'update:loading'
]);

// 组件状态
const message = useMessage();
const isOpen = ref(false);
const batchFormRef = ref<FormInst | null>(null);

// 批量操作表单
const batchForm = reactive({
  operation: 'edit',
  class_id: null as number | null,
  category: null as string | null,
  status: null as string | null,
  tags: [] as string[],
  confirmDelete: false,
  exportFormat: 'xlsx',
  customFields: {}
});

// 操作选项
const operationOptions = computed(() => {
  const options = [
    { label: '批量编辑', value: 'edit' },
    { label: '批量删除', value: 'delete' },
    { label: '批量导出', value: 'export' }
  ];
  
  // 如果有自定义插槽，添加自定义操作选项
  if (slots.customBatchFields) {
    options.push({ label: '自定义操作', value: 'custom' });
  }
  
  return options;
});

// 表单是否有效
const isValid = computed(() => {
  if (props.selectedItems.length === 0) {
    return false;
  }
  
  if (batchForm.operation === 'edit') {
    // 编辑操作至少需要一个字段有值
    return batchForm.class_id !== null || 
           batchForm.category !== null || 
           batchForm.status !== null || 
           batchForm.tags.length > 0;
  }
  
  if (batchForm.operation === 'delete') {
    // 删除操作需要确认
    return batchForm.confirmDelete;
  }
  
  return true;
});

// 监听选中项变化
watch(() => props.selectedItems, (newVal) => {
  if (newVal.length === 0 && isOpen.value) {
    message.warning('没有选中的项目');
  }
}, { deep: true });

// 处理操作类型变更
const handleOperationChange = () => {
  // 重置表单值
  if (batchForm.operation === 'edit') {
    batchForm.class_id = null;
    batchForm.category = null;
    batchForm.status = null;
    batchForm.tags = [];
  } else if (batchForm.operation === 'delete') {
    batchForm.confirmDelete = false;
  } else if (batchForm.operation === 'export') {
    batchForm.exportFormat = 'xlsx';
  }
};

// 开启批量操作
const openBatchOperation = () => {
  isOpen.value = true;
  emit('open');
};

// 关闭批量操作
const closeBatchOperation = () => {
  isOpen.value = false;
  resetBatchForm();
  emit('close');
};

// 重置表单
const resetBatchForm = () => {
  batchForm.operation = 'edit';
  batchForm.class_id = null;
  batchForm.category = null;
  batchForm.status = null;
  batchForm.tags = [];
  batchForm.confirmDelete = false;
  batchForm.exportFormat = 'xlsx';
  batchForm.customFields = {};
};

// 应用批量操作
const handleApplyBatch = () => {
  if (!isValid.value) {
    return;
  }
  
  emit('update:loading', true);
  
  const payload: {
    operation: string;
    items: any[];
    data: Record<string, any>;
  } = {
    operation: batchForm.operation,
    items: props.selectedItems.map(item => item.id || item),
    data: {}
  };
  
  if (batchForm.operation === 'edit') {
    if (batchForm.class_id !== null) payload.data.class_id = batchForm.class_id;
    if (batchForm.category !== null) payload.data.category = batchForm.category;
    if (batchForm.status !== null) payload.data.status = batchForm.status;
    if (batchForm.tags.length > 0) payload.data.tags = batchForm.tags;
  } else if (batchForm.operation === 'export') {
    payload.data.format = batchForm.exportFormat;
  } else if (batchForm.operation === 'custom') {
    payload.data = { ...batchForm.customFields };
  }
  
  emit('apply-batch', payload);
};

// 获取插槽
const slots = defineSlots<{
  customBatchFields?: (props: {}) => any;
}>();
</script>

<style scoped>
.batch-operation-panel {
  width: 100%;
  margin-bottom: 16px;
}

.batch-content {
  min-height: 100px;
}

.batch-placeholder {
  min-height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 14px;
}

.selected-summary {
  margin-top: 8px;
}

.selected-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.operation-options {
  margin-top: 12px;
}
</style> 