<template>
  <n-modal
    v-model:show="showModal"
    :title="isEdit ? '编辑量化项目' : '创建量化项目'"
    preset="card"
    :style="{ width: '500px' }"
    :mask-closable="false"
    @close="handleCancel"
  >
    <n-form
      ref="formRef"
      :model="formModel"
      :rules="rules"
      label-placement="left"
      label-width="80"
      require-mark-placement="right-hanging"
    >
      <n-form-item path="name" label="名称">
        <n-input
          v-model:value="formModel.name"
          placeholder="请输入量化项目名称"
        />
      </n-form-item>
      
      <n-form-item path="category" label="分类">
        <n-select
          v-model:value="formModel.category"
          placeholder="请选择分类"
          :options="categoryOptions"
          tag
          filterable
        />
      </n-form-item>
      
      <n-form-item path="default_score" label="默认分值">
        <n-input-number
          v-model:value="formModel.default_score"
          :min="-10"
          :max="10"
          :step="0.5"
          placeholder="请输入默认分值"
          style="width: 100%"
        />
      </n-form-item>
      
      <n-form-item path="description" label="描述">
        <n-input
          v-model:value="formModel.description"
          type="textarea"
          placeholder="请输入项目描述"
          :autosize="{ minRows: 3, maxRows: 5 }"
        />
      </n-form-item>
      
      <n-form-item path="is_active" label="状态">
        <n-switch
          v-model:value="formModel.is_active"
          checked-value={true}
          unchecked-value={false}
        >
          <template #checked>启用</template>
          <template #unchecked>停用</template>
        </n-switch>
      </n-form-item>
    </n-form>
    
    <template #footer>
      <div class="flex justify-end">
        <n-button @click="handleCancel" class="mr-2">取消</n-button>
        <n-button type="primary" :loading="submitting" @click="handleSubmit">
          {{ isEdit ? '保存' : '创建' }}
        </n-button>
      </div>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch, computed } from 'vue';
import { 
  NModal, NForm, NFormItem, NInput, NSelect, NInputNumber,
  NSwitch, NButton, useMessage
} from 'naive-ui';
import { createQuantItem, updateQuantItem, getQuantItems } from '@/services/api/quant-items';

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  quantItem: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['update:show', 'success']);
const message = useMessage();

const showModal = computed({
  get: () => props.show,
  set: (value) => emit('update:show', value)
});

const isEdit = computed(() => !!props.quantItem);
const formRef = ref(null);
const submitting = ref(false);
const categoryOptions = ref([
  { label: '纪律', value: '纪律' },
  { label: '卫生', value: '卫生' },
  { label: '学习', value: '学习' },
  { label: '活动', value: '活动' }
]);

const formModel = reactive({
  name: '',
  category: '',
  default_score: 0,
  description: '',
  is_active: true
});

const rules = {
  name: [
    { required: true, message: '请输入项目名称', trigger: 'blur' },
    { min: 2, max: 50, message: '名称长度在2到50个字符之间', trigger: 'blur' }
  ],
  category: [
    { required: true, message: '请选择或输入分类', trigger: 'blur' }
  ],
  default_score: [
    { required: true, message: '请输入默认分值', type: 'number', trigger: 'blur' }
  ]
};

watch(() => props.quantItem, () => {
  if (props.quantItem) {
    // 编辑模式，设置表单初始值
    Object.keys(formModel).forEach(key => {
      if (props.quantItem[key] !== undefined) {
        formModel[key] = props.quantItem[key];
      }
    });
  } else {
    // 创建模式，重置表单
    resetForm();
  }
}, { immediate: true });

onMounted(async () => {
  await fetchCategories();
});

const fetchCategories = async () => {
  try {
    const response = await getQuantItems();
    const items = response.data;
    
    // 提取已有的分类
    const categories = new Set(items.map(item => item.category));
    
    // 合并到已有选项中
    const existingValues = categoryOptions.value.map(option => option.value);
    categories.forEach(category => {
      if (!existingValues.includes(category)) {
        categoryOptions.value.push({ label: category, value: category });
      }
    });
  } catch (error) {
    console.error('Failed to fetch categories:', error);
  }
};

const resetForm = () => {
  formModel.name = '';
  formModel.category = '';
  formModel.default_score = 0;
  formModel.description = '';
  formModel.is_active = true;
  
  if (formRef.value) {
    formRef.value.resetValidation();
  }
};

const handleSubmit = (e) => {
  e.preventDefault();
  formRef.value?.validate(async (errors) => {
    if (errors) return;
    
    submitting.value = true;
    
    try {
      if (isEdit.value) {
        // 更新量化项目
        await updateQuantItem(props.quantItem.id, formModel);
        message.success('量化项目更新成功');
      } else {
        // 创建量化项目
        await createQuantItem(formModel);
        message.success('量化项目创建成功');
      }
      
      // 关闭模态框并通知父组件刷新数据
      showModal.value = false;
      emit('success');
      resetForm();
    } catch (error) {
      console.error('Failed to save quant item:', error);
      message.error(isEdit.value ? '更新量化项目失败' : '创建量化项目失败');
    } finally {
      submitting.value = false;
    }
  });
};

const handleCancel = () => {
  showModal.value = false;
  resetForm();
};
</script>
