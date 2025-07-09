<template>
  <n-modal
    v-model:show="showModal"
    :title="isEdit ? '编辑量化记录' : '创建量化记录'"
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
      <n-form-item path="student_id" label="学生">
        <n-select
          v-model:value="formModel.student_id"
          placeholder="选择学生"
          :options="studentOptions"
          :disabled="isEdit"
          filterable
        />
      </n-form-item>
      
      <n-form-item path="item_id" label="量化项目">
        <n-select
          v-model:value="formModel.item_id"
          placeholder="选择量化项目"
          :options="itemOptions"
          filterable
          @update:value="handleItemChange"
        />
      </n-form-item>
      
      <n-form-item path="score" label="分值">
        <n-input-number
          v-model:value="formModel.score"
          :min="-10"
          :max="10"
          :step="0.5"
          style="width: 100%"
        />
      </n-form-item>
      
      <n-form-item path="reason" label="原因">
        <n-input
          v-model:value="formModel.reason"
          type="textarea"
          placeholder="请输入记录原因"
          :autosize="{ minRows: 3, maxRows: 5 }"
        />
      </n-form-item>
      
      <n-form-item path="record_date" label="日期">
        <n-date-picker
          v-model:value="formModel.record_date"
          type="date"
          :is-date-disabled="disableFutureDates"
          style="width: 100%"
        />
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
import { ref, reactive, computed, watch } from 'vue';
import { 
  NModal, NForm, NFormItem, NSelect, NInputNumber,
  NInput, NDatePicker, NButton, useMessage
} from 'naive-ui';
import dayjs from 'dayjs';
import { createQuantRecord, updateQuantRecord } from '@/services/api/quant-records';

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  record: {
    type: Object,
    default: null
  },
  studentOptions: {
    type: Array,
    default: () => []
  },
  itemOptions: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits(['update:show', 'success']);
const message = useMessage();

const showModal = computed({
  get: () => props.show,
  set: (value) => emit('update:show', value)
});

const isEdit = computed(() => !!props.record);
const formRef = ref(null);
const submitting = ref(false);

const formModel = reactive({
  student_id: null,
  item_id: null,
  score: 0,
  reason: '',
  record_date: Date.now()
});

const rules = {
  student_id: [
    { required: true, message: '请选择学生', trigger: 'blur' }
  ],
  item_id: [
    { required: true, message: '请选择量化项目', trigger: 'blur' }
  ],
  score: [
    { required: true, message: '请输入分值', type: 'number', trigger: 'blur' }
  ],
  record_date: [
    { required: true, message: '请选择日期', type: 'number', trigger: 'blur' }
  ]
};

watch(() => props.record, () => {
  if (props.record) {
    // 编辑模式，设置表单初始值
    formModel.student_id = props.record.student_id;
    formModel.item_id = props.record.item_id;
    formModel.score = Number(props.record.score);
    formModel.reason = props.record.reason || '';
    formModel.record_date = new Date(props.record.record_date).getTime();
  } else {
    // 创建模式，重置表单
    resetForm();
  }
}, { immediate: true });

const resetForm = () => {
  formModel.student_id = null;
  formModel.item_id = null;
  formModel.score = 0;
  formModel.reason = '';
  formModel.record_date = Date.now();
  
  if (formRef.value) {
    formRef.value.resetValidation();
  }
};

const handleItemChange = (value) => {
  // 当选择量化项目时，自动填充默认分值
  if (value) {
    const selectedItem = props.itemOptions.find(item => item.value === value);
    if (selectedItem && selectedItem.default_score !== undefined) {
      formModel.score = selectedItem.default_score;
    }
  }
};

const disableFutureDates = (ts: number) => {
  return ts > Date.now();
};

const handleSubmit = (e) => {
  e.preventDefault();
  formRef.value?.validate(async (errors) => {
    if (errors) return;
    
    submitting.value = true;
    
    try {
      const payload = {
        student_id: formModel.student_id,
        item_id: formModel.item_id,
        score: formModel.score,
        reason: formModel.reason,
        record_date: dayjs(formModel.record_date).format('YYYY-MM-DD')
      };
      
      if (isEdit.value) {
        // 更新量化记录
        await updateQuantRecord(props.record.id, payload);
        message.success('量化记录更新成功');
      } else {
        // 创建量化记录
        await createQuantRecord(payload);
        message.success('量化记录创建成功');
      }
      
      // 关闭模态框并通知父组件刷新数据
      showModal.value = false;
      emit('success');
      resetForm();
    } catch (error) {
      console.error('Failed to save record:', error);
      message.error(isEdit.value ? '更新量化记录失败' : '创建量化记录失败');
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
