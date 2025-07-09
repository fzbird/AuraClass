<template>
  <div>
    <div class="flex justify-between mb-6">
      <h1 class="text-2xl font-bold">创建量化记录</h1>
      
      <n-button @click="$router.go(-1)">
        返回
      </n-button>
    </div>
    
    <n-card>
      <n-form
        ref="formRef"
        :model="formModel"
        :rules="rules"
        label-placement="left"
        label-width="120"
        require-mark-placement="right-hanging"
      >
        <n-form-item path="class_id" label="班级">
          <n-select
            v-model:value="formModel.class_id"
            placeholder="选择班级"
            :options="classOptions"
            @update:value="handleClassChange"
          />
        </n-form-item>
        
        <n-form-item path="student_id" label="学生">
          <n-select
            v-model:value="formModel.student_id"
            placeholder="选择学生"
            filterable
            :options="studentOptions"
            :loading="loadingStudents"
          />
        </n-form-item>
        
        <n-form-item path="item_id" label="量化项目">
          <n-select
            v-model:value="formModel.item_id"
            placeholder="选择量化项目"
            filterable
            :options="itemOptions"
            :loading="loadingItems"
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
            placeholder="记录原因（选填）"
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
        
        <n-form-item>
          <n-space justify="end">
            <n-button @click="$router.go(-1)">取消</n-button>
            <n-button type="primary" :loading="submitting" @click="handleSubmit">
              创建
            </n-button>
          </n-space>
        </n-form-item>
      </n-form>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { 
  NButton, NCard, NForm, NFormItem, NSelect, NInputNumber,
  NInput, NDatePicker, NSpace, useMessage
} from 'naive-ui';
import dayjs from 'dayjs';
import { getStudents } from '@/services/api/students';
import { getClasses } from '@/services/api/classes';
import { getQuantItems } from '@/services/api/quant-items';
import { createQuantRecord } from '@/services/api/quant-records';

const router = useRouter();
const message = useMessage();

const formRef = ref(null);
const submitting = ref(false);
const classOptions = ref([]);
const studentOptions = ref([]);
const itemOptions = ref([]);
const loadingStudents = ref(false);
const loadingItems = ref(false);

const formModel = reactive({
  class_id: null,
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

onMounted(async () => {
  await Promise.all([
    fetchClasses(),
    fetchQuantItems()
  ]);
});

const fetchClasses = async () => {
  try {
    const response = await getClasses();
    classOptions.value = response.data.map(cls => ({
      label: cls.name,
      value: cls.id
    }));
  } catch (error) {
    console.error('Failed to fetch classes:', error);
    message.error('获取班级列表失败');
  }
};

const fetchStudents = async (classId) => {
  loadingStudents.value = true;
  try {
    const response = await getStudents({ class_id: classId });
    studentOptions.value = response.data.map(student => ({
      label: `${student.student_id_no} - ${student.full_name}`,
      value: student.id
    }));
  } catch (error) {
    console.error('Failed to fetch students:', error);
    message.error('获取学生列表失败');
  } finally {
    loadingStudents.value = false;
  }
};

const fetchQuantItems = async () => {
  loadingItems.value = true;
  try {
    const response = await getQuantItems();
    itemOptions.value = response.data
      .filter(item => item.is_active)
      .map(item => ({
        label: `${item.name} (${item.default_score})`,
        value: item.id,
        category: item.category,
        default_score: item.default_score
      }));
  } catch (error) {
    console.error('Failed to fetch quant items:', error);
    message.error('获取量化项目失败');
  } finally {
    loadingItems.value = false;
  }
};

const handleClassChange = (value) => {
  formModel.student_id = null;
  if (value) {
    fetchStudents(value);
  } else {
    studentOptions.value = [];
  }
};

const handleItemChange = (value) => {
  if (value) {
    const selectedItem = itemOptions.value.find(item => item.value === value);
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
      
      await createQuantRecord(payload);
      message.success('量化记录创建成功');
      
      // 返回列表页
      router.push('/records');
    } catch (error) {
      console.error('Failed to create record:', error);
      message.error('创建量化记录失败');
    } finally {
      submitting.value = false;
    }
  });
};
</script>
