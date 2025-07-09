<template>
  <div>
    <n-form
      ref="formRef"
      inline
      :model="formModel"
      label-placement="left"
      label-width="auto"
      require-mark-placement="right-hanging"
      @submit.prevent="handleSubmit"
    >
      <n-form-item label="学号" path="student_id_no">
        <n-input
          v-model:value="formModel.student_id_no"
          placeholder="请输入学号"
          clearable
        />
      </n-form-item>
      
      <n-form-item label="姓名" path="name">
        <n-input
          v-model:value="formModel.name"
          placeholder="请输入姓名"
          clearable
        />
      </n-form-item>
      
      <n-form-item label="班级" path="class_id">
        <n-select
          v-model:value="formModel.class_id"
          :options="classOptions"
          placeholder="请选择班级"
          clearable
          style="min-width: 150px"
        />
      </n-form-item>
      
      <n-form-item label="性别" path="gender">
        <n-select
          v-model:value="formModel.gender"
          :options="genderOptions"
          placeholder="请选择性别"
          clearable
          style="min-width: 120px"
        />
      </n-form-item>
      
      <n-form-item>
        <n-space>
          <n-button type="primary" attr-type="submit">
            搜索
          </n-button>
          <n-button @click="resetFilter">
            重置
          </n-button>
        </n-space>
      </n-form-item>
    </n-form>
  </div>
</template>

<script setup lang="ts">
import { ref, defineProps, defineEmits } from 'vue';
import { NForm, NFormItem, NInput, NSelect, NButton, NSpace } from 'naive-ui';

const props = defineProps({
  classOptions: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits(['filter']);

const formRef = ref(null);

const formModel = ref({
  student_id_no: '',
  name: '',
  class_id: null,
  gender: null
});

const genderOptions = [
  { label: '男', value: 'male' },
  { label: '女', value: 'female' }
];

const handleSubmit = () => {
  const params = {};
  
  // 只添加有值的字段
  Object.keys(formModel.value).forEach(key => {
    const value = formModel.value[key];
    if (value !== null && value !== undefined && value !== '') {
      // 将class_id映射为classId以匹配StudentsPage.vue中的filterParams
      if (key === 'class_id') {
        params['classId'] = value;
      } else {
        params[key] = value;
      }
    }
  });
  
  console.log('提交搜索条件:', params);
  emit('filter', params);
};

const resetFilter = () => {
  // 重置表单
  formModel.value = {
    student_id_no: '',
    name: '',
    class_id: null,
    gender: null
  };
  
  // 触发搜索，使用空对象重置筛选条件
  emit('filter', {});
};
</script> 