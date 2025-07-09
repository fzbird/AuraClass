<template>
  <n-form
    ref="formRef"
    :model="formModel"
    :rules="rules"
    label-placement="left"
    label-width="80"
    require-mark-placement="right-hanging"
  >
    <n-grid :cols="24" :x-gap="24">
      <!-- 学生选择 -->
      <n-gi :span="24">
        <n-form-item path="student_id" label="学生">
          <n-select
            v-model:value="formModel.student_id"
            filterable
            placeholder="请选择学生"
            :options="studentOptions"
            :loading="loadingStudents"
            @update:value="handleStudentChange"
            :disabled="!!record"
          />
        </n-form-item>
      </n-gi>
      
      <!-- 量化项目选择 -->
      <n-gi :span="24">
        <n-form-item path="item_id" label="量化项目">
          <n-select
            v-model:value="formModel.item_id"
            :options="itemOptions"
            filterable
            :disabled="submitting"
            placeholder="请选择量化项目"
            @update:value="handleItemChange"
          />
        </n-form-item>
      </n-gi>
      
      <!-- 分数输入 -->
      <n-gi :span="12">
        <n-form-item path="score" label="得分">
          <n-input-number
            v-model:value="formModel.score"
            placeholder="请输入分数"
            class="w-full"
            :disabled="submitting"
            :max="100"
            :min="-100"
          />
        </n-form-item>
      </n-gi>
      
      <!-- 记录日期选择 -->
      <n-gi :span="12">
        <n-form-item path="record_date" label="记录日期">
          <n-date-picker
            v-model:value="formModel.record_date"
            type="date"
            clearable
            style="width: 100%"
          />
        </n-form-item>
      </n-gi>
      
      <!-- 原因输入 -->
      <n-gi :span="24">
        <n-form-item path="reason" label="原因">
          <n-input
            v-model:value="formModel.reason"
            type="textarea"
            placeholder="请输入量化原因"
            :rows="3"
          />
        </n-form-item>
      </n-gi>
    </n-grid>
    
    <!-- 表单按钮 -->
    <div class="flex justify-end mt-4">
      <n-space>
        <n-button @click="handleCancel">取消</n-button>
        <n-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ record ? '保存' : '创建' }}
        </n-button>
      </n-space>
    </div>
  </n-form>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch, nextTick } from 'vue';
import type { PropType } from 'vue';
import { 
  NForm,
  NFormItem,
  NGrid,
  NGi,
  NSelect,
  NInputNumber,
  NInput,
  NButton,
  NSpace,
  NDatePicker,
  useMessage,
  type FormInst,
  type FormRules,
  type FormItemRule,
  type SelectOption
} from 'naive-ui';
import { getStudents } from '@/services/api/students';
import { getQuantItems } from '@/services/api/quant-items';
import { createQuantRecord, updateQuantRecord } from '@/services/api/records';
import type { QuantRecord, CreateQuantRecordPayload } from '@/types/record';
import type { QuantItem } from '@/types/quant-item';
import { useUserStore } from '@/stores/user';
import { FileResponse } from 'fastapi';
import { export_stats } from '@/services/export';

// 定义组件属性
const props = defineProps<{
  record?: Record<string, any>;
}>();

// 定义组件事件
const emit = defineEmits(['success', 'cancel']);

// 表单和消息实例
const formRef = ref<FormInst | null>(null);
const message = useMessage();

// 数据加载和提交状态
const loadingStudents = ref(false);
const loadingItems = ref(false);
const submitting = ref(false);

// 选项数据
const students = ref<{ id: number; student_id_no: string; full_name: string }[]>([]);
const items = ref<QuantItem[]>([]);

// 表单模型数据
interface RecordFormModel {
  student_id: number;
  item_id: number;
  score: number;
  reason: string;
  record_date: number | null;
}

const formModel = reactive<RecordFormModel>({
  student_id: props.record?.student_id ?? 0,
  item_id: props.record?.item_id ?? 0,
  score: props.record?.score ?? 0,
  reason: props.record?.reason ?? '',
  record_date: props.record ? new Date(props.record.record_date).getTime() : Date.now()
});

// 表单验证规则
const rules: FormRules = {
  student_id: [
    { 
      required: true, 
      message: '请选择学生', 
      trigger: ['blur', 'change'],
      validator: (rule, value) => value !== null && value !== undefined && value !== 0
    }
  ],
  item_id: [
    { 
      required: true, 
      message: '请选择量化项目', 
      trigger: ['blur', 'change'],
      validator: (rule, value) => value !== null && value !== undefined && value !== 0
    }
  ],
  score: [
    { 
      required: true, 
      message: '请输入分数', 
      trigger: ['blur', 'change'],
      validator: (rule, value) => value !== null && value !== undefined
    },
    { type: 'number', message: '分数必须为数字', trigger: ['blur', 'change'] }
  ],
  record_date: [
    { 
      required: true, 
      message: '请选择记录日期', 
      trigger: ['blur', 'change'],
      validator: (rule, value) => value !== null && value !== undefined
    }
  ],
  reason: [
    {
      required: true,
      message: '请输入量化原因',
      trigger: ['blur', 'change'],
      validator: (rule, value) => value !== null && value !== undefined && value.trim() !== ''
    }
  ]
};

// 计算属性：学生选项
const studentOptions = computed<SelectOption[]>(() => {
  return students.value.map(student => ({
    label: `${student.student_id_no} - ${student.full_name}`,
    value: student.id
  }));
});

// 计算属性：量化项目选项
const itemOptions = computed<SelectOption[]>(() => {
  return items.value.map(item => ({
    label: `${item.name} (${item.default_score ?? 0}) ${item.category ? `- ${item.category}` : ''}`,
    value: item.id,
    category: item.category,
    default_score: item.default_score ?? 0
  }));
});

// 加载学生数据
const loadStudents = async () => {
  loadingStudents.value = true;
  try {
    const response = await getStudents({ page_size: 500 });
    if (response.data && response.data.data) {
      students.value = response.data.data;
    }
  } catch (error) {
    console.error('Failed to load students:', error);
    message.error('加载学生数据失败');
  } finally {
    loadingStudents.value = false;
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

// 学生变更处理
const handleStudentChange = (value: number) => {
  formModel.student_id = value;
};

// 量化项目变更处理
const handleItemChange = (value: number) => {
  console.log('量化项目变更为:', value);
  if (!value) return;

  if (props.record) {
    // 编辑模式下，不自动设置默认分数，但需确保显示原始分数
    console.log('编辑模式下保持原始分数:', props.record.score);
    nextTick(() => {
      formModel.score = props.record.score;
    });
  } else {
    // 创建模式下，设置默认分数和原因
    const selectedItem = items.value.find(item => item.id === value);
    if (selectedItem) {
      formModel.score = selectedItem.default_score || 0;
      if (selectedItem.default_reason && !formModel.reason) {
        formModel.reason = selectedItem.default_reason;
      }
    }
  }
};

// 提交表单
const handleSubmit = () => {
  console.log('提交表单，当前值:', formModel);

  // 手动验证关键字段是否有值
  if (!formModel.student_id || formModel.student_id === 0) {
    message.error('请选择学生');
    return;
  }
  
  if (!formModel.item_id || formModel.item_id === 0) {
    message.error('请选择量化项目');
    return;
  }
  
  if (formModel.score === undefined || formModel.score === null) {
    message.error('请输入分数');
    return;
  }
  
  if (!formModel.record_date) {
    message.error('请选择记录日期');
    return;
  }
  
  // 验证原因字段不为空
  if (!formModel.reason || formModel.reason.trim() === '') {
    message.error('请输入原因');
    return;
  }
  
  submitting.value = true;
  
  try {
    // 使用useUserStore获取当前用户信息
    const userStore = useUserStore();
    let recorder_id = 1; // 默认为1，以防无法获取用户ID
    
    // 从用户store中获取当前用户ID
    if (userStore.user && userStore.user.id) {
      recorder_id = userStore.user.id;
    }
    
    // 格式化日期为ISO字符串并截取日期部分
    const recordDate = formModel.record_date 
      ? new Date(formModel.record_date).toISOString().split('T')[0]
      : new Date().toISOString().split('T')[0];
    
    // 准备提交数据
    const payload: CreateQuantRecordPayload = {
      student_id: formModel.student_id,
      item_id: formModel.item_id,
      score: formModel.score,
      reason: formModel.reason.trim(), // 确保去除首尾空格
      record_date: recordDate,
      recorder_id: recorder_id // 添加记录人ID
    };
    
    console.log('提交数据:', payload);
    
    // 创建或更新记录
    if (props.record) {
      updateQuantRecord(props.record.id, payload)
        .then(() => {
          message.success('记录更新成功');
          emit('success');
        })
        .catch((error) => {
          console.error('更新记录失败:', error);
          message.error('更新记录失败: ' + (error.message || '未知错误'));
        })
        .finally(() => {
          submitting.value = false;
        });
    } else {
      createQuantRecord(payload)
        .then(() => {
          message.success('记录创建成功');
          emit('success');
        })
        .catch((error) => {
          console.error('创建记录失败:', error);
          message.error('创建记录失败: ' + (error.message || '未知错误'));
        })
        .finally(() => {
          submitting.value = false;
        });
    }
  } catch (error) {
    console.error('处理表单数据失败:', error);
    message.error('保存记录失败');
    submitting.value = false;
  }
};

// 取消操作
const handleCancel = () => {
  emit('cancel');
};

// 组件挂载时加载数据
onMounted(() => {
  loadStudents();
  loadItems();
});

// 添加重置表单的方法，以支持从模板填充数据
const resetForm = (values: { item_id?: number; score?: number; reason?: string }) => {
  // 如果在编辑模式下，不应重置表单
  if (props.record) {
    console.log('编辑模式下不重置表单');
    return;
  }
  
  if (values) {
    formModel.item_id = values.item_id !== undefined ? values.item_id : 0;
    formModel.score = values.score !== undefined ? values.score : 0;
    formModel.reason = values.reason || '';
    
    // 如果有项目ID，尝试加载项目信息
    if (values.item_id) {
      const selectedItem = items.value.find(item => item.id === values.item_id);
      if (selectedItem) {
        formModel.score = selectedItem.default_score || values.score || 0;
      }
    }
  }
};

// 监听初始值变化
watch(
  () => props.initialValues,
  (newValues) => {
    // 在编辑模式下，不应用初始值
    if (props.record) {
      console.log('编辑模式下忽略初始值变化');
      return;
    }
    
    if (newValues) {
      resetForm(newValues);
    }
  },
  { immediate: true }
);

// 当编辑模式下记录变更时，更新表单数据
watch(() => props.record, (newRecord) => {
  if (newRecord) {
    console.log('编辑记录，原始数据:', newRecord);
    
    // 直接使用新的对象替换formModel中的值，而不是一个个设置
    Object.assign(formModel, {
      student_id: newRecord.student_id,
      item_id: newRecord.item_id,
      score: newRecord.score,
      reason: newRecord.reason,
      record_date: new Date(newRecord.record_date).getTime()
    });
    
    // 确保在编辑模式下显示正确的分数
    console.log('设置表单分数为:', newRecord.score);
    
    // 延迟一帧确保UI更新，并用两层nextTick确保分数被正确设置
    nextTick(() => {
      formModel.score = newRecord.score;
      nextTick(() => {
        formModel.score = newRecord.score;
      });
    });
  }
}, { immediate: true, deep: true });

// 确保在编辑模式下，当项目更改时不覆盖原始分数
watch(() => formModel.item_id, (newItemId, oldItemId) => {
  if (props.record && oldItemId) {
    // 如果在编辑模式且项目ID更改，保持原始分数不变
    console.log('编辑模式下项目ID更改，保持原始分数:', props.record.score);
    nextTick(() => {
      formModel.score = props.record.score;
    });
  }
}, { immediate: false });

// 将resetForm方法暴露给父组件
defineExpose({
  resetForm
});
</script>

<style scoped>
.mt-4 {
  margin-top: 16px;
}

.flex {
  display: flex;
}

.justify-end {
  justify-content: flex-end;
}
</style> 