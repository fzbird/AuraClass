<template>
  <div class="record-template">
    <n-card title="记录模板管理" :bordered="false">
      <template #header-extra>
        <n-button type="primary" @click="showCreateModal = true">
          <template #icon>
            <n-icon><PlusOutlined /></n-icon>
          </template>
          创建模板
        </n-button>
      </template>

      <!-- 模板列表 -->
      <n-data-table
        :columns="columns"
        :data="templates"
        :loading="loading"
        :pagination="{ pageSize: 5 }"
        :row-key="row => row.id"
      />

      <!-- 创建模板对话框 -->
      <n-modal v-model:show="showCreateModal" :mask-closable="false" preset="card" title="创建记录模板" style="width: 600px;">
        <n-form
          ref="createFormRef"
          :model="createForm"
          :rules="rules"
          label-placement="left"
          label-width="auto"
          require-mark-placement="right-hanging"
        >
          <n-form-item label="模板名称" path="name">
            <n-input v-model:value="createForm.name" placeholder="输入模板名称" />
          </n-form-item>
          
          <n-form-item label="量化项目" path="item_id">
            <n-select
              v-model:value="createForm.item_id"
              filterable
              clearable
              placeholder="选择量化项目"
              :options="itemOptions"
              :loading="loadingItems"
            />
          </n-form-item>
          
          <n-form-item label="分数" path="score">
            <n-input-number
              v-model:value="createForm.score"
              placeholder="输入分数"
              :min="-100"
              :max="100"
              style="width: 100%;"
            />
          </n-form-item>
          
          <n-form-item label="原因" path="reason">
            <n-input
              v-model:value="createForm.reason"
              type="textarea"
              placeholder="输入记录原因"
              :autosize="{ minRows: 3, maxRows: 5 }"
            />
          </n-form-item>
          
          <n-form-item label="描述" path="description">
            <n-input
              v-model:value="createForm.description"
              type="textarea"
              placeholder="输入模板描述（可选）"
              :autosize="{ minRows: 2, maxRows: 3 }"
            />
          </n-form-item>
          
          <n-space justify="end">
            <n-button @click="showCreateModal = false">取消</n-button>
            <n-button type="primary" @click="handleCreateTemplate" :loading="saving">保存</n-button>
          </n-space>
        </n-form>
      </n-modal>
      
      <!-- 使用模板确认对话框 -->
      <n-modal v-model:show="showUseModal" preset="dialog" title="使用模板" positive-text="确认" negative-text="取消" @positive-click="confirmUseTemplate" @negative-click="cancelUseTemplate">
        <template #icon>
          <n-icon><QuestionCircleOutlined /></n-icon>
        </template>
        <div class="use-template-confirm">
          <p>确定要使用模板 <strong>{{ selectedTemplate?.name }}</strong> 创建新记录吗？</p>
          <div class="template-details">
            <p><strong>量化项目:</strong> {{ selectedTemplate?.item_name }}</p>
            <p><strong>分数:</strong> {{ selectedTemplate?.score }}</p>
            <p><strong>原因:</strong> {{ selectedTemplate?.reason }}</p>
          </div>
        </div>
      </n-modal>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, h } from 'vue';
import {
  NCard,
  NButton,
  NDataTable,
  NSpace,
  NModal,
  NForm,
  NFormItem,
  NInput,
  NInputNumber,
  NSelect,
  NIcon,
  useMessage,
  type DataTableColumns,
  type FormInst,
  type FormRules
} from 'naive-ui';
import PlusOutlined from '@vicons/antd/es/PlusOutlined';
import EditOutlined from '@vicons/antd/es/EditOutlined';
import DeleteOutlined from '@vicons/antd/es/DeleteOutlined';
import QuestionCircleOutlined from '@vicons/antd/es/QuestionCircleOutlined';
import { 
  getRecordTemplates, 
  createRecordTemplate, 
  updateRecordTemplate, 
  deleteRecordTemplate 
} from '@/services/api/record-templates';
import { getQuantItems } from '@/services/api/quant-items';
import type { SelectOption } from 'naive-ui';
import type { RecordTemplate } from '@/types/record';

// Props
const props = defineProps<{
  userId: number;
}>();

// Emits
const emit = defineEmits<{
  (e: 'use-template', template: RecordTemplate): void;
}>();

// 组件状态
const message = useMessage();
const templates = ref<RecordTemplate[]>([]);
const loading = ref(false);
const saving = ref(false);
const loadingItems = ref(false);
const showCreateModal = ref(false);
const showUseModal = ref(false);
const selectedTemplate = ref<RecordTemplate | null>(null);
const createFormRef = ref<FormInst | null>(null);

// 表单数据
const createForm = ref({
  name: '',
  item_id: null as number | null,
  score: 0,
  reason: '',
  description: ''
});

// 表单验证规则
const rules: FormRules = {
  name: [
    { required: true, message: '请输入模板名称', trigger: 'blur' }
  ],
  item_id: [
    { required: true, message: '请选择量化项目', trigger: ['blur', 'change'] }
  ],
  score: [
    { required: true, message: '请输入分数', trigger: ['blur', 'change'] }
  ],
  reason: [
    { required: true, message: '请输入记录原因', trigger: 'blur' }
  ]
};

// 数据源
const items = ref<{ id: number; name: string; category?: string }[]>([]);

// 构建量化项目选项
const itemOptions = computed<SelectOption[]>(() => 
  items.value.map(item => ({
    label: `${item.name}${item.category ? ` (${item.category})` : ''}`,
    value: item.id
  }))
);

// 表格列定义
const columns = computed<DataTableColumns>(() => [
  {
    title: '模板名称',
    key: 'name'
  },
  {
    title: '量化项目',
    key: 'item_name'
  },
  {
    title: '分数',
    key: 'score',
    render: (row) => {
      const rowData = row as unknown as RecordTemplate;
      const scoreClass = rowData.score > 0 ? 'positive-score' : rowData.score < 0 ? 'negative-score' : '';
      return h('span', { class: scoreClass }, String(rowData.score));
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
    title: '操作',
    key: 'actions',
    render: (row) => {
      const rowData = row as unknown as RecordTemplate;
      return h(NSpace, {}, {
        default: () => [
          h(NButton, {
            quaternary: true,
            size: 'small',
            onClick: () => handleUseTemplate(rowData)
          }, {
            default: () => '使用',
          }),
          h(NButton, {
            quaternary: true,
            size: 'small',
            onClick: () => handleEditTemplate(rowData)
          }, {
            default: () => '编辑',
            icon: () => h(EditOutlined)
          }),
          h(NButton, {
            quaternary: true,
            size: 'small',
            onClick: () => handleDeleteTemplate(rowData)
          }, {
            default: () => '删除',
            icon: () => h(DeleteOutlined)
          })
        ]
      });
    }
  }
]);

// 加载模板数据
const loadTemplates = async () => {
  loading.value = true;
  try {
    const response = await getRecordTemplates({ user_id: props.userId });
    if (response.data && response.data.data) {
      templates.value = response.data.data;
    }
  } catch (error) {
    console.error('Failed to load templates:', error);
    message.error('加载记录模板失败');
  } finally {
    loading.value = false;
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

// 创建模板
const handleCreateTemplate = () => {
  createFormRef.value?.validate(async (errors) => {
    if (!errors) {
      saving.value = true;
      try {
        // 找到选中的项目名称
        const selectedItem = items.value.find(item => item.id === createForm.value.item_id);
        
        const payload = {
          user_id: props.userId,
          name: createForm.value.name,
          item_id: createForm.value.item_id as number,
          item_name: selectedItem?.name || '',
          score: createForm.value.score,
          reason: createForm.value.reason,
          description: createForm.value.description || ''
        };
        
        const response = await createRecordTemplate(payload);
        if (response.data && response.data.data) {
          message.success('模板创建成功');
          showCreateModal.value = false;
          resetForm();
          loadTemplates();
        }
      } catch (error) {
        console.error('Failed to create template:', error);
        message.error('创建模板失败');
      } finally {
        saving.value = false;
      }
    }
  });
};

// 使用模板
const handleUseTemplate = (template: RecordTemplate) => {
  selectedTemplate.value = template;
  showUseModal.value = true;
};

// 确认使用模板
const confirmUseTemplate = () => {
  if (selectedTemplate.value) {
    emit('use-template', selectedTemplate.value);
  }
  showUseModal.value = false;
};

// 取消使用模板
const cancelUseTemplate = () => {
  selectedTemplate.value = null;
  showUseModal.value = false;
};

// 编辑模板
const handleEditTemplate = (template: RecordTemplate) => {
  // 在实际应用中，这里会打开编辑模态框并填充数据
  message.info('编辑功能待实现');
};

// 删除模板
const handleDeleteTemplate = async (template: RecordTemplate) => {
  try {
    await deleteRecordTemplate(template.id);
    message.success('模板删除成功');
    loadTemplates();
  } catch (error) {
    console.error('Failed to delete template:', error);
    message.error('删除模板失败');
  }
};

// 重置表单
const resetForm = () => {
  createForm.value = {
    name: '',
    item_id: null,
    score: 0,
    reason: '',
    description: ''
  };
};

// 组件挂载时加载数据
onMounted(() => {
  loadTemplates();
  loadItems();
});
</script>

<style scoped>
.record-template {
  width: 100%;
}

.template-details {
  margin-top: 10px;
  padding: 10px;
  background-color: #f5f5f5;
  border-radius: 4px;
}

.positive-score {
  color: #18a058;
  font-weight: bold;
}

.negative-score {
  color: #d03050;
  font-weight: bold;
}

.use-template-confirm {
  padding: 0 12px;
}
</style> 