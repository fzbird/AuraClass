<template>
  <n-modal
    v-model:show="showModal"
    title="批量录入量化记录"
    preset="card"
    style="width: 800px; max-width: 90vw"
    :mask-closable="false"
    @close="handleCancel"
  >
    <div class="mb-4">
      <div class="flex justify-between items-center mb-4">
        <n-form-item label="班级" class="mb-0 mr-4">
          <n-select
            v-model:value="selectedClass"
            placeholder="选择班级"
            :options="classOptions"
            @update:value="handleClassChange"
          />
        </n-form-item>
        
        <n-form-item label="量化项目" class="mb-0 mr-4 flex-1">
          <n-select
            v-model:value="selectedItem"
            placeholder="选择量化项目"
            :options="itemOptions"
            @update:value="handleItemChange"
          />
        </n-form-item>
        
        <n-form-item label="日期" class="mb-0">
          <n-date-picker
            v-model:value="recordDate"
            type="date"
            :is-date-disabled="disableFutureDates"
          />
        </n-form-item>
      </div>
      
      <div class="flex items-center mb-4">
        <n-checkbox v-model:checked="selectAll" @update:checked="handleSelectAll">
          全选
        </n-checkbox>
        
        <n-input-number
          v-model:value="batchScore"
          :min="-10"
          :max="10"
          :step="0.5"
          class="ml-4"
          placeholder="批量设置分值"
        >
          <template #prefix>
            分值：
          </template>
        </n-input-number>
        
        <n-input
          v-model:value="batchReason"
          class="ml-4 flex-1"
          placeholder="批量设置原因"
        >
          <template #prefix>
            原因：
          </template>
        </n-input>
        
        <n-button
          type="primary"
          class="ml-4"
          :disabled="!selectedItem || !selectedClass"
          @click="applyBatchSettings"
        >
          应用
        </n-button>
      </div>
    </div>
    
    <div class="max-h-96 overflow-y-auto">
      <n-data-table
        :columns="columns"
        :data="studentRecords"
        :bordered="false"
        :single-line="false"
        size="small"
      />
    </div>
    
    <template #footer>
      <div class="flex justify-end">
        <n-button @click="handleCancel" class="mr-2">取消</n-button>
        <n-button 
          type="primary" 
          :loading="submitting" 
          :disabled="!hasSelectedRecords"
          @click="handleSubmit"
        >
          保存
        </n-button>
      </div>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, computed, reactive, h, watch } from 'vue';
import { 
  NModal, NFormItem, NSelect, NDatePicker, NInputNumber, 
  NCheckbox, NInput, NButton, NDataTable, useMessage 
} from 'naive-ui';
import dayjs from 'dayjs';
import { getStudents } from '@/services/api/students';
import { createBatchQuantRecords } from '@/services/api/quant-records';

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  classOptions: {
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

const selectedClass = ref(null);
const selectedItem = ref(null);
const recordDate = ref(Date.now());
const selectAll = ref(false);
const batchScore = ref(0);
const batchReason = ref('');
const submitting = ref(false);
const studentRecords = ref([]);
const loading = ref(false);

const columns = [
  {
    type: 'selection',
    multiple: true
  },
  {
    title: '学号',
    key: 'student_id_no'
  },
  {
    title: '姓名',
    key: 'full_name'
  },
  {
    title: '分值',
    key: 'score',
    render: (row) => {
      return h(
        NInputNumber,
        {
          value: row.score,
          min: -10,
          max: 10,
          step: 0.5,
          size: 'small',
          style: { width: '100px' },
          onUpdateValue: (value) => {
            row.score = value;
          }
        }
      );
    }
  },
  {
    title: '原因',
    key: 'reason',
    render: (row) => {
      return h(
        NInput,
        {
          value: row.reason,
          size: 'small',
          onUpdateValue: (value) => {
            row.reason = value;
          }
        }
      );
    }
  }
];

const handleClassChange = async (value) => {
  if (!value) {
    studentRecords.value = [];
    return;
  }
  
  loading.value = true;
  try {
    const response = await getStudents({ class_id: value });
    
    studentRecords.value = response.data.map(student => ({
      id: student.id,
      student_id: student.id,
      student_id_no: student.student_id_no,
      full_name: student.full_name,
      score: 0,
      reason: '',
      checked: false
    }));
  } catch (error) {
    console.error('Failed to fetch students:', error);
    message.error('获取班级学生失败');
  } finally {
    loading.value = false;
  }
};

const handleItemChange = (value) => {
  if (!value) return;
  
  const selectedItemObj = props.itemOptions.find(item => item.value === value);
  if (selectedItemObj && selectedItemObj.default_score !== undefined) {
    batchScore.value = selectedItemObj.default_score;
  }
};

const disableFutureDates = (ts: number) => {
  return ts > Date.now();
};

const handleSelectAll = (checked) => {
  studentRecords.value.forEach(record => {
    record.checked = checked;
  });
};

const applyBatchSettings = () => {
  studentRecords.value.forEach(record => {
    if (record.checked) {
      record.score = batchScore.value;
      record.reason = batchReason.value;
    }
  });
};

const hasSelectedRecords = computed(() => {
  return studentRecords.value.some(record => record.checked && record.score !== null);
});

const handleSubmit = async () => {
  if (!selectedItem.value || !selectedClass.value || !recordDate.value) {
    message.warning('请选择量化项目、班级和日期');
    return;
  }
  
  if (!hasSelectedRecords.value) {
    message.warning('请至少选择一条记录');
    return;
  }
  
  submitting.value = true;
  
  try {
    const selectedRecords = studentRecords.value
      .filter(record => record.checked && record.score !== null)
      .map(record => ({
        student_id: record.student_id,
        item_id: selectedItem.value,
        score: record.score,
        reason: record.reason,
        record_date: dayjs(recordDate.value).format('YYYY-MM-DD')
      }));
    
    await createBatchQuantRecords(selectedRecords);
    message.success(`成功录入 ${selectedRecords.length} 条量化记录`);
    
    // 关闭模态框并通知父组件刷新数据
    showModal.value = false;
    emit('success');
    resetForm();
  } catch (error) {
    console.error('Failed to create batch records:', error);
    message.error('批量录入量化记录失败');
  } finally {
    submitting.value = false;
  }
};

const handleCancel = () => {
  showModal.value = false;
  resetForm();
};

const resetForm = () => {
  selectedClass.value = null;
  selectedItem.value = null;
  recordDate.value = Date.now();
  selectAll.value = false;
  batchScore.value = 0;
  batchReason.value = '';
  studentRecords.value = [];
};

// 监听表格选择状态变化
watch(
  () => studentRecords.value.map(record => record.checked),
  (newCheckedStates) => {
    const allChecked = newCheckedStates.every(checked => checked);
    const someChecked = newCheckedStates.some(checked => checked);
    
    selectAll.value = allChecked && newCheckedStates.length > 0;
  },
  { deep: true }
);
</script>
