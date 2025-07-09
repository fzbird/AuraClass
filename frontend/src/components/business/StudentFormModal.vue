<template>
  <n-modal
    v-model:show="showModal"
    :mask-closable="false"
    preset="dialog"
    :title="student ? '编辑学生' : '添加学生'"
    :positive-text="student ? '保存修改' : '确认添加'"
    negative-text="取消"
    @positive-click="handleSubmit"
    @negative-click="handleCancel"
    :loading="loading"
    :positive-button-props="{ disabled: !formValidated }"
  >
    <n-form
      ref="formRef"
      :model="formModel"
      :rules="rules"
      label-placement="left"
      label-width="80"
      require-mark-placement="right-hanging"
      style="max-width: 640px"
    >
      <n-form-item label="学号" path="student_id_no">
        <n-input
          v-model:value="formModel.student_id_no"
          placeholder="请输入学号"
        />
      </n-form-item>
      
      <n-form-item label="姓名" path="full_name">
        <n-input
          v-model:value="formModel.full_name"
          placeholder="请输入姓名"
        />
      </n-form-item>
      
      <n-form-item label="班级" path="class_id">
        <n-select
          v-model:value="formModel.class_id"
          :options="classOptions"
          placeholder="请选择班级"
          clearable
        />
      </n-form-item>
      
      <n-form-item label="性别" path="gender">
        <n-radio-group v-model:value="formModel.gender">
          <n-space>
            <n-radio value="male">男</n-radio>
            <n-radio value="female">女</n-radio>
          </n-space>
        </n-radio-group>
      </n-form-item>
      
      <n-form-item label="出生日期" path="birth_date">
        <n-date-picker
          v-model:value="formModel.birth_date"
          type="date"
          placeholder="请选择出生日期"
          clearable
        />
      </n-form-item>
      
      <n-form-item label="电话" path="phone">
        <n-input
          v-model:value="formModel.phone"
          placeholder="请输入联系电话"
        />
      </n-form-item>
      
      <n-form-item label="邮箱" path="email">
        <n-input
          v-model:value="formModel.email"
          placeholder="请输入电子邮箱"
        />
      </n-form-item>
      
      <n-form-item label="联系信息" path="contact_info">
        <n-input
          v-model:value="formModel.contact_info"
          type="textarea"
          placeholder="其他联系信息"
        />
      </n-form-item>

      <n-form-item v-if="student" label="状态" path="is_active">
        <n-switch
          v-model:value="formModel.is_active"
          :round="false"
        >
          <template #checked>启用</template>
          <template #unchecked>禁用</template>
        </n-switch>
      </n-form-item>
    </n-form>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, defineProps, defineEmits, onMounted, watch } from 'vue';
import { 
  NModal, 
  NForm, 
  NFormItem, 
  NInput, 
  NSelect, 
  NRadioGroup, 
  NRadio, 
  NSpace,
  NDatePicker,
  NSwitch,
  FormInst as FormInstType,
  useMessage,
  type FormRules,
  type SelectOption 
} from 'naive-ui';
import { createStudent, updateStudent } from '@/services/api/students';
import type { Student, CreateStudentPayload, UpdateStudentPayload } from '@/types/student';

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  student: {
    type: Object as () => Student | null,
    default: null
  },
  classOptions: {
    type: Array as () => SelectOption[],
    default: () => []
  }
});

const emit = defineEmits(['update:show', 'success']);

const message = useMessage();
const showModal = ref(props.show);
const loading = ref(false);
const formRef = ref<FormInstType | null>(null);
const formValidated = ref(false); // 追踪表单验证状态

// Form model
const defaultFormState = {
  student_id_no: '',
  full_name: '',
  class_id: null as number | null,
  gender: 'male', // Default gender
  birth_date: undefined as number | undefined, // 出生日期字段使用数字类型
  phone: '',
  email: '',
  contact_info: '', // 替换notes字段
  is_active: true // 新增激活状态字段
};

const formModel = ref({ ...defaultFormState });

// Form validation rules
const rules: FormRules = {
  student_id_no: [
    { required: true, message: '请输入学号', trigger: 'blur' },
    { type: 'string', max: 20, message: '学号长度不能超过20个字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_-]+$/, message: '学号只能包含字母、数字、下划线和连字符', trigger: 'blur' }
  ],
  full_name: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { type: 'string', max: 50, message: '姓名长度不能超过50个字符', trigger: 'blur' }
  ],
  class_id: [
    { required: true, type: 'number', message: '请选择班级', trigger: ['blur', 'change'] }
  ],
  gender: [
    { required: true, message: '请选择性别', trigger: ['blur', 'change'] }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入有效的手机号码', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入有效的电子邮箱', trigger: 'blur' }
  ]
};

// Watch for prop changes
watch(() => props.show, (newVal) => {
  showModal.value = newVal;
});

watch(() => showModal.value, (newVal) => {
  emit('update:show', newVal);
});

// 在这里定义resetForm函数，确保它在watch使用之前已定义
const resetForm = () => {
  formModel.value = { ...defaultFormState };
  if (formRef.value) {
    formRef.value.restoreValidation();
  }
};

// 在这里添加一个函数用于类型转换
const formatDateString = (date: any): string | undefined => {
  if (!date) return undefined;
  
  try {
    // 转换为Date对象
    const dateObj = new Date(date);
    // 检查是否为有效日期
    if (isNaN(dateObj.getTime())) return undefined;
    
    // 提取年月日并格式化为YYYY-MM-DD
    const year = dateObj.getFullYear();
    const month = String(dateObj.getMonth() + 1).padStart(2, '0');
    const day = String(dateObj.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  } catch (e) {
    console.error('日期格式化错误:', e);
    return undefined;
  }
};

// 将字符串日期转为时间戳
const parseDate = (dateStr: string | undefined): number | undefined => {
  if (!dateStr) return undefined;
  try {
    return new Date(dateStr).getTime();
  } catch (e) {
    console.error('日期解析错误:', e);
    return undefined;
  }
};

watch(() => props.student, (newVal) => {
  if (newVal) {
    // Fill form with student data when editing
    formModel.value = {
      student_id_no: newVal.student_id_no || '',
      full_name: newVal.full_name || '',
      class_id: newVal.class_id || null,
      gender: newVal.gender || 'male',
      // 保持日期为时间戳数字格式，这是DatePicker期望的
      birth_date: newVal.birth_date ? parseDate(newVal.birth_date) : undefined,
      phone: newVal.phone || '',
      email: newVal.email || '',
      contact_info: newVal.contact_info || '',
      is_active: newVal.is_active !== undefined ? newVal.is_active : true
    };
    console.log('加载学生数据:', formModel.value);
  } else {
    // Reset form when creating new student
    resetForm();
  }
}, { immediate: true });

// 表单数据变化时重新验证
watch(() => formModel.value, () => {
  validateForm();
}, { deep: true });

// 当模态框打开时执行验证
watch(() => showModal.value, (newVal) => {
  if (newVal) {
    // 给表单一点时间渲染
    setTimeout(() => {
      validateForm();
    }, 100);
  }
});

// 验证表单
const validateForm = () => {
  if (!formRef.value) {
    formValidated.value = false;
    return;
  }
  
  formRef.value.validate((errors) => {
    // 只有没有错误且日期有效时才算验证通过
    formValidated.value = !errors && 
      (formModel.value.birth_date ? isValidDate(formModel.value.birth_date) : true);
  })
  .catch(() => {
    formValidated.value = false;
  });
};

// Form submission
const handleSubmit = (e?: MouseEvent) => {
  if (e) {
    e.preventDefault();
  }
  
  if (!formRef.value) return;
  
  // 先手动触发验证以显示所有字段错误
  formRef.value.validate(async (errors: any) => {
    if (errors) {
      console.error('表单验证失败:', errors);
      
      // 提取第一个错误消息
      let firstErrorMsg = '表单验证失败，请检查填写内容';
      if (errors && errors.length > 0 && errors[0] && errors[0].length > 0) {
        firstErrorMsg = errors[0][0].message || firstErrorMsg;
      }
      
      // 显示验证错误并阻止提交
      message.error(firstErrorMsg);
      return;
    }
    
    // 手动验证日期 (如果需要日期)
    if (formModel.value.birth_date && !isValidDate(formModel.value.birth_date)) {
      message.error('请选择有效的出生日期');
      return;
    }
    
    // 显示加载状态
    loading.value = true;
    
    try {
      // 处理表单数据
      console.log('提交表单数据:', formModel.value);
      
      // 格式化日期
      const formattedDate = formatDateString(formModel.value.birth_date);
      console.log('格式化后的日期:', formattedDate);
      
      const formData = { 
        ...formModel.value,
        class_id: formModel.value.class_id as number,
        birth_date: formattedDate
      };
      
      if (props.student) {
        // Update existing student
        await updateStudent(props.student.id, formData);
        message.success('学生信息更新成功');
      } else {
        // Create new student
        await createStudent(formData);
        message.success('学生添加成功');
      }
      
      // Close modal and notify parent
      showModal.value = false;
      emit('success');
      resetForm();
    } catch (error: any) {
      console.error('Failed to save student:', error);
      
      // 提供更详细的错误反馈
      let errorMsg = props.student ? '更新学生信息失败' : '添加学生失败';
      
      // 检查是否有详细错误信息
      if (error.response?.data?.error) {
        const apiError = error.response.data.error;
        
        // 处理验证错误
        if (apiError.code === 'VALIDATION_ERROR' && apiError.details?.length > 0) {
          const detail = apiError.details[0];
          
          // 根据错误类型提供友好提示
          if (detail.type === 'date_from_datetime_inexact') {
            errorMsg = '日期格式错误: 请选择有效的日期';
          } else if (detail.loc?.includes('student_id_no')) {
            errorMsg = '学号错误: ' + (detail.msg || '不符合要求');
          } else if (detail.loc?.includes('full_name')) {
            errorMsg = '姓名错误: ' + (detail.msg || '不符合要求');
          } else if (detail.loc?.includes('email')) {
            errorMsg = '邮箱格式错误: ' + (detail.msg || '不符合要求');
          } else if (detail.loc?.includes('phone')) {
            errorMsg = '电话号码错误: ' + (detail.msg || '不符合要求');
          } else {
            // 其他字段错误
            const field = detail.loc?.[detail.loc.length - 1] || '未知字段';
            errorMsg = `${field}错误: ${detail.msg || '数据验证失败'}`;
          }
        }
        // 显示API返回的错误信息
        else if (apiError.message) {
          errorMsg = apiError.message;
        }
      }
      
      message.error(errorMsg);
    } finally {
      loading.value = false;
    }
  });
};

const handleCancel = () => {
  showModal.value = false;
  resetForm();
};

// 检查日期是否有效
const isValidDate = (date: any): boolean => {
  if (!date) return true; // 如果日期为空则视为有效（非必填）
  
  try {
    // 尝试创建日期对象
    const dateObj = new Date(date);
    // 检查是否为有效日期
    return !isNaN(dateObj.getTime());
  } catch (e) {
    console.error('日期验证错误:', e);
    return false;
  }
};
</script> 