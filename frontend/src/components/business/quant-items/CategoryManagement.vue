<template>
  <div>
    <n-space align="center" justify="end" class="mb-4">
      <n-button type="primary" @click="handleAddNew">
        添加分类
      </n-button>
    </n-space>

    <n-data-table
      :columns="columns"
      :data="categories"
      :loading="loading"
      :pagination="pagination"
    />

    <n-modal
      v-model:show="showFormModal"
      :mask-closable="false"
      preset="card"
      :title="modalTitle"
      style="width: 450px"
    >
      <n-form
        ref="formRef"
        :model="formModel"
        :rules="formRules"
        label-placement="left"
        label-width="80"
        require-mark-placement="right-hanging"
      >
        <n-form-item label="分类名称" path="name">
          <n-input v-model:value="formModel.name" placeholder="请输入分类名称" />
        </n-form-item>
        <n-form-item label="描述" path="description">
          <n-input
            v-model:value="formModel.description"
            placeholder="请输入分类描述"
            type="textarea"
            :autosize="{ minRows: 3, maxRows: 5 }"
          />
        </n-form-item>
        <n-form-item label="排序" path="order">
          <n-input-number
            v-model:value="formModel.order"
            :min="0"
            placeholder="请输入排序值（越小越靠前）"
          />
        </n-form-item>
        <n-form-item label="状态" path="is_active">
          <n-switch v-model:value="formModel.is_active" />
        </n-form-item>
      </n-form>

      <template #footer>
        <n-space justify="end">
          <n-button @click="closeForm">取消</n-button>
          <n-button type="primary" :loading="submitLoading" @click="handleSubmit">
            确定
          </n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { h, ref, computed } from 'vue';
import { 
  NButton, 
  NSpace, 
  NTag, 
  NSwitch, 
  NForm, 
  NFormItem, 
  NInput,
  NInputNumber,
  useMessage 
} from 'naive-ui';
import type { 
  QuantItemCategory, 
  CreateQuantItemCategoryPayload, 
  UpdateQuantItemCategoryPayload 
} from '@/types/quant-item';

// 自定义类型定义
interface FormInst {
  validate: (callback?: (errors?: Array<string>) => void) => Promise<void>;
  restoreValidation: () => void;
}

interface FormRule {
  required?: boolean;
  validator?: (rule: FormRule, value: any) => boolean | Error | Promise<boolean | Error>;
  trigger?: string | string[];
  message?: string;
  renderMessage?: () => any;
}

interface FormRules {
  [path: string]: FormRule | Array<FormRule> | undefined;
}

// Props
interface Props {
  categories: QuantItemCategory[];
  loading?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  loading: false
});

// Emits
const emit = defineEmits<{
  (e: 'add', data: CreateQuantItemCategoryPayload): void;
  (e: 'edit', id: number, data: UpdateQuantItemCategoryPayload): void;
  (e: 'delete', id: number): void;
  (e: 'cancel'): void;
}>();

// State
const formRef = ref<FormInst | null>(null);
const showFormModal = ref(false);
const submitLoading = ref(false);
const editingCategory = ref<QuantItemCategory | null>(null);

const formModel = ref<CreateQuantItemCategoryPayload>({
  name: '',
  description: '',
  order: 0,
  is_active: true
});

const formRules: FormRules = {
  name: [
    { required: true, message: '请输入分类名称', trigger: 'blur' }
  ]
};

// Computed
const modalTitle = computed(() => 
  editingCategory.value ? '编辑分类' : '添加分类'
);

const pagination = {
  pageSize: 5,
  showSizePicker: false,
  itemCount: props.categories.length,
  prefix: ({ itemCount }: { itemCount: number }) => `共 ${itemCount} 条`
};

// Table columns
const columns = [
  {
    title: '分类名称',
    key: 'name',
    width: 150
  },
  {
    title: '描述',
    key: 'description',
    ellipsis: {
      tooltip: true
    }
  },
  {
    title: '排序',
    key: 'order',
    width: 80
  },
  {
    title: '状态',
    key: 'is_active',
    width: 100,
    render: (row: QuantItemCategory) => h(
      NTag,
      { type: row.is_active ? 'success' : 'error' },
      { default: () => row.is_active ? '启用' : '禁用' }
    )
  },
  {
    title: '操作',
    key: 'actions',
    width: 150,
    render: (row: QuantItemCategory) => h(
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
              type: 'error',
              onClick: () => handleDelete(row)
            },
            { default: () => '删除' }
          )
        ]
      }
    )
  }
];

// Methods
const message = useMessage();

const resetForm = () => {
  formModel.value = {
    name: '',
    description: '',
    order: 0,
    is_active: true
  };
  editingCategory.value = null;
  if (formRef.value) {
    formRef.value.restoreValidation();
  }
};

const closeForm = () => {
  showFormModal.value = false;
  resetForm();
};

const handleAddNew = () => {
  resetForm();
  showFormModal.value = true;
};

const handleEdit = (category: QuantItemCategory) => {
  editingCategory.value = category;
  formModel.value = {
    name: category.name,
    description: category.description || '',
    order: category.order || 0,
    is_active: category.is_active
  };
  showFormModal.value = true;
};

const handleDelete = (category: QuantItemCategory) => {
  emit('delete', category.id);
};

const handleSubmit = () => {
  formRef.value?.validate((errors) => {
    if (errors) {
      return;
    }

    try {
      submitLoading.value = true;
      
      if (editingCategory.value) {
        emit('edit', editingCategory.value.id, formModel.value);
      } else {
        emit('add', formModel.value);
      }
      
      closeForm();
    } finally {
      submitLoading.value = false;
    }
  });
};

const cancel = () => {
  emit('cancel');
};
</script> 