<template>
  <div>
    <n-form ref="formRef" :model="formModel" :rules="rules" label-placement="left" :label-width="80">
      <n-form-item label="学生" path="studentId">
        <n-select
          v-model:value="formModel.studentId"
          filterable
          placeholder="选择学生"
          :options="studentOptions"
          :loading="loadingStudents"
        />
      </n-form-item>
      
      <n-form-item label="量化项目" path="itemId">
        <n-select
          v-model:value="formModel.itemId"
          filterable
          placeholder="选择量化项目"
          :options="itemOptions"
          :loading="loadingItems"
          @update:value="handleItemChange"
        />
      </n-form-item>
      
      <n-form-item label="分数" path="score">
        <n-input-number
          v-model:value="formModel.score"
          :min="currentMinScore"
          :max="currentMaxScore"
          :step="1"
        />
        <span class="text-xs text-gray-500 ml-2" v-if="currentItem">
          ({{ currentMinScore }}~{{ currentMaxScore }})
        </span>
      </n-form-item>
      
      <n-form-item label="原因" path="reason">
        <n-input
          v-model:value="formModel.reason"
          type="textarea"
          placeholder="请简要说明原因"
          :autosize="{ minRows: 2, maxRows: 4 }"
        />
      </n-form-item>
      
      <n-form-item>
        <n-button type="primary" @click="handleSubmit" :loading="submitting">
          提交记录
        </n-button>
        <n-button class="ml-4" @click="resetForm">
          重置
        </n-button>
      </n-form-item>
    </n-form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';
import { NForm, NFormItem, NSelect, NInputNumber, NInput, NButton } from 'naive-ui';
import type { FormInst, FormRules, SelectOption } from 'naive-ui';
import { createRecord } from '@/services/api/records';
import { getStudents } from '@/services/api/students';
import { getQuantItems } from '@/services/api/quant-items';
import type { Student } from '@/types/student';
import type { QuantItem } from '@/types/quant-item';

// 定义表单数据类型
interface RecordFormModel {
  studentId: number | null;
  itemId: number | null;
  score: number;
  reason: string;
}

// 定义事件
const emit = defineEmits(['success']);

// 表单引用
const formRef = ref<FormInst | null>(null);

// 状态
const submitting = ref(false);
const loadingStudents = ref(false);
const loadingItems = ref(false);
const students = ref<Student[]>([]);
const quantItems = ref<QuantItem[]>([]);

// 表单数据
const formModel = reactive<RecordFormModel>({
  studentId: null,
  itemId: null,
  score: 0,
  reason: ''
});

// 表单验证规则
const rules: FormRules = {
  studentId: {
    required: true,
    type: 'number',
    message: '请选择学生',
    trigger: ['blur', 'change']
  },
  itemId: {
    required: true,
    type: 'number',
    message: '请选择量化项目',
    trigger: ['blur', 'change']
  },
  score: {
    required: true,
    type: 'number',
    message: '请输入分数',
    trigger: ['blur', 'change']
  },
  reason: {
    required: true,
    message: '请简要说明原因',
    trigger: ['blur', 'input']
  }
};

// 学生选项
const studentOptions = computed<SelectOption[]>(() => 
  students.value.map(student => ({
    label: student.fullName,
    value: student.id
  }))
);

// 量化项目选项
const itemOptions = computed<SelectOption[]>(() => 
  quantItems.value.filter(item => item.isActive).map(item => ({
    label: `${item.name} (${item.category})`,
    value: item.id
  }))
);

// 当前选中的量化项目
const currentItem = computed(() => 
  quantItems.value.find(item => item.id === formModel.itemId)
);

// 当前最小分数
const currentMinScore = computed(() => 
  currentItem.value ? currentItem.value.minScore : 0
);

// 当前最大分数
const currentMaxScore = computed(() => 
  currentItem.value ? currentItem.value.maxScore : 100
);

// 处理量化项目变更
const handleItemChange = (itemId: number) => {
  if (!itemId) return;
  
  const item = quantItems.value.find(item => item.id === itemId);
  if (item) {
    formModel.score = item.baseScore;
  }
};

// 提交表单
const handleSubmit = () => {
  if (!formRef.value) return;
  
  formRef.value.validate(async (errors) => {
    if (errors) return;
    
    submitting.value = true;
    
    try {
      // 确保所有必填字段都有值
      if (!formModel.studentId || !formModel.itemId) {
        throw new Error('请完成表单必填项');
      }
      
      await createRecord({
        studentId: formModel.studentId,
        itemId: formModel.itemId,
        score: formModel.score,
        reason: formModel.reason
      });
      
      emit('success');
      resetForm();
    } catch (error) {
      console.error('Failed to create record:', error);
    } finally {
      submitting.value = false;
    }
  });
};

// 重置表单
const resetForm = () => {
  formModel.studentId = null;
  formModel.itemId = null;
  formModel.score = 0;
  formModel.reason = '';
  
  if (formRef.value) {
    formRef.value.restoreValidation();
  }
};

// 获取学生列表
const fetchStudents = async () => {
  loadingStudents.value = true;
  
  try {
    const response = await getStudents();
    students.value = response.data || [];
  } catch (error) {
    console.error('Failed to fetch students:', error);
  } finally {
    loadingStudents.value = false;
  }
};

// 获取量化项目列表
const fetchItems = async () => {
  loadingItems.value = true;
  
  try {
    const response = await getQuantItems({ isActive: true });
    quantItems.value = response.items || [];
  } catch (error) {
    console.error('Failed to fetch quant items:', error);
  } finally {
    loadingItems.value = false;
  }
};

// 组件挂载时加载数据
onMounted(() => {
  fetchStudents();
  fetchItems();
});
</script>
