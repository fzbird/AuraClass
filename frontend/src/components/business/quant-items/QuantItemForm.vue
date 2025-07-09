<template>
  <n-form
    ref="formRef"
    :model="formModel"
    :rules="rules"
    label-placement="left"
    label-width="auto"
    require-mark-placement="right-hanging"
    size="medium"
    :style="{ maxWidth: '640px' }"
  >
    <n-form-item label="项目名称" path="name">
      <n-input v-model:value="formModel.name" placeholder="请输入量化项目名称" />
    </n-form-item>

    <n-form-item label="项目分类" path="category">
      <n-select
        v-model:value="formModel.category"
        :options="categoryOptions"
        placeholder="请选择项目分类"
      />
    </n-form-item>

    <n-form-item label="项目描述" path="description">
      <n-input
        v-model:value="formModel.description"
        type="textarea"
        placeholder="请输入项目描述"
      />
    </n-form-item>

    <n-form-item label="默认分值" path="default_score">
      <n-input-number
        v-model:value="formModel.default_score"
        :min="formModel.min_score"
        :max="formModel.max_score"
        :precision="1"
        placeholder="请输入默认分值"
      />
    </n-form-item>

    <n-form-item label="最小分值" path="min_score">
      <n-input-number
        v-model:value="formModel.min_score"
        :max="formModel.default_score"
        :precision="1"
        :min="-100.0"
        placeholder="请输入最小分值（可为负数）"
      />
    </n-form-item>

    <n-form-item label="最大分值" path="max_score">
      <n-input-number
        v-model:value="formModel.max_score"
        :min="formModel.default_score"
        :precision="1"
        :max="100.0"
        placeholder="请输入最大分值"
      />
    </n-form-item>

    <n-form-item label="权重" path="weight">
      <n-input-number
        v-model:value="formModel.weight"
        :min="0"
        :max="10"
        :precision="1"
        placeholder="请输入权重"
      />
    </n-form-item>

    <n-form-item label="默认原因" path="default_reason">
      <n-input
        v-model:value="formModel.default_reason"
        type="textarea"
        placeholder="请输入默认原因（可选）"
      />
    </n-form-item>

    <n-form-item label="启用状态" path="is_active">
      <n-switch v-model:value="formModel.is_active" />
    </n-form-item>

    <div class="flex justify-end gap-4">
      <n-button @click="handleReset">重置</n-button>
      <n-button type="primary" :loading="loading" @click="handleSubmit">
        {{ submitButtonText }}
      </n-button>
    </div>
  </n-form>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { NForm } from 'naive-ui'
import type { QuantItem, CreateQuantItemPayload, QuantItemCategory } from '@/types/quant-item'
import { useQuantItemStore } from '@/stores/quant-item'

const props = defineProps<{
  initialData?: Partial<QuantItem>
  loading?: boolean
}>()

const emit = defineEmits<{
  (e: 'submit', data: CreateQuantItemPayload): void
}>()

const quantItemStore = useQuantItemStore()
const formRef = ref<{ validate: () => Promise<void>, restoreValidation: () => void } | null>(null)

function toNumber(value: any): number {
  if (value === null || value === undefined) return 0;
  if (typeof value === 'number') return value;
  const parsed = Number(value);
  return isNaN(parsed) ? 0 : parsed;
}

const processedInitialData = computed(() => {
  if (!props.initialData) return null;
  
  return {
    ...props.initialData,
    default_score: toNumber(props.initialData.default_score),
    min_score: toNumber(props.initialData.min_score),
    max_score: toNumber(props.initialData.max_score),
    weight: toNumber(props.initialData.weight)
  };
});

const formModel = ref<CreateQuantItemPayload>({
  name: props.initialData?.name ?? '',
  category: props.initialData?.category ?? '',
  description: props.initialData?.description ?? '',
  default_score: toNumber(props.initialData?.default_score),
  max_score: toNumber(props.initialData?.max_score) || 100,
  min_score: toNumber(props.initialData?.min_score) || -10,
  weight: toNumber(props.initialData?.weight) || 1,
  default_reason: props.initialData?.default_reason ?? '未设置',
  is_active: props.initialData?.is_active ?? true
});

watch(() => props.initialData, (newData) => {
  if (newData) {
    formModel.value = {
      name: newData.name ?? '',
      category: newData.category ?? '',
      description: newData.description ?? '',
      default_score: toNumber(newData.default_score),
      max_score: toNumber(newData.max_score) || 100,
      min_score: toNumber(newData.min_score) || -10,
      weight: toNumber(newData.weight) || 1,
      default_reason: newData.default_reason ?? '未设置',
      is_active: newData.is_active ?? true
    };
  }
}, { immediate: true });

const categoryOptions = computed(() => 
  quantItemStore.categories.map((category: QuantItemCategory) => ({
    label: category.name,
    value: category.name
  }))
)

const submitButtonText = computed(() => 
  props.initialData?.id ? '更新' : '创建'
)

const rules = {
  name: {
    required: true,
    message: '请输入项目名称',
    trigger: ['blur', 'input']
  },
  category: {
    required: true,
    message: '请选择项目分类',
    trigger: ['blur', 'change']
  },
  description: {
    required: true,
    message: '请输入项目描述',
    trigger: ['blur', 'input']
  },
  default_score: [
    {
      type: 'number',
      required: true,
      message: '请输入默认分值',
      trigger: ['blur', 'change']
    },
    {
      type: 'number',
      validator: (_rule: any, value: any) => value !== null && value !== undefined,
      message: '请输入默认分值',
      trigger: ['blur', 'change']
    }
  ],
  max_score: [
    {
      type: 'number',
      required: true,
      message: '请输入最大分值',
      trigger: ['blur', 'change']
    },
    {
      type: 'number',
      validator: (_rule: any, value: any) => value !== null && value !== undefined,
      message: '请输入最大分值',
      trigger: ['blur', 'change']
    }
  ],
  min_score: [
    {
      type: 'number',
      required: true,
      message: '请输入最小分值',
      trigger: ['blur', 'change']
    },
    {
      type: 'number',
      validator: (_rule: any, value: any) => value !== null && value !== undefined,
      message: '请输入最小分值',
      trigger: ['blur', 'change']
    }
  ],
  weight: [
    {
      type: 'number',
      required: true,
      message: '请输入权重',
      trigger: ['blur', 'change']
    },
    {
      type: 'number',
      validator: (_rule: any, value: any) => value !== null && value !== undefined,
      message: '请输入权重',
      trigger: ['blur', 'change']
    }
  ]
}

const handleSubmit = async (e: MouseEvent) => {
  e.preventDefault()
  try {
    // 在验证前确保所有数值字段都是数字类型
    formModel.value.default_score = toNumber(formModel.value.default_score);
    formModel.value.min_score = toNumber(formModel.value.min_score);
    formModel.value.max_score = toNumber(formModel.value.max_score);
    formModel.value.weight = toNumber(formModel.value.weight);
    
    console.log('验证前数据:', JSON.stringify(formModel.value));
    
    // 手动检查数值字段
    if (
      formModel.value.default_score === undefined || 
      formModel.value.min_score === undefined || 
      formModel.value.max_score === undefined || 
      formModel.value.weight === undefined
    ) {
      console.error('数值字段验证失败：存在undefined值');
      return;
    }
    
    await formRef.value?.validate()
    console.log('提交表单数据:', formModel.value);
    emit('submit', formModel.value)
  } catch (error) {
    console.error('Form validation failed:', error)
  }
}

const handleReset = () => {
  formRef.value?.restoreValidation()
  if (processedInitialData.value?.id) {
    Object.assign(formModel.value, {
      name: processedInitialData.value.name ?? '',
      category: processedInitialData.value.category ?? '',
      description: processedInitialData.value.description ?? '',
      default_score: toNumber(processedInitialData.value.default_score),
      max_score: toNumber(processedInitialData.value.max_score),
      min_score: toNumber(processedInitialData.value.min_score),
      weight: toNumber(processedInitialData.value.weight),
      default_reason: processedInitialData.value.default_reason ?? '未设置',
      is_active: processedInitialData.value.is_active ?? true
    })
  } else {
    Object.assign(formModel.value, {
      name: '',
      category: '',
      description: '',
      default_score: 0,
      max_score: 100,
      min_score: -10,
      weight: 1,
      default_reason: '未设置',
      is_active: true
    })
  }
}
</script> 