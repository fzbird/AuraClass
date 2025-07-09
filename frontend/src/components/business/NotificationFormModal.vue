<template>
  <n-modal
    v-model:show="showModal"
    title="创建通知"
    preset="card"
    :style="{ width: '500px' }"
    :mask-closable="false"
  >
    <n-form
      ref="formRef"
      :model="formModel"
      :rules="rules"
      label-placement="left"
      label-width="80"
      require-mark-placement="right-hanging"
    >
      <n-form-item path="title" label="标题">
        <n-input
          v-model:value="formModel.title"
          placeholder="请输入通知标题"
          maxlength="50"
          show-count
        />
      </n-form-item>
      
      <n-form-item path="content" label="内容">
        <n-input
          v-model:value="formModel.content"
          type="textarea"
          placeholder="请输入通知内容"
          :autosize="{ minRows: 4, maxRows: 8 }"
          maxlength="500"
          show-count
        />
      </n-form-item>
      
      <n-form-item path="recipient_type" label="接收者">
        <n-radio-group v-model:value="formModel.recipient_type">
          <n-space>
            <n-radio value="all">全部用户</n-radio>
            <n-radio value="class">指定班级</n-radio>
            <n-radio value="user">指定用户</n-radio>
          </n-space>
        </n-radio-group>
      </n-form-item>
      
      <n-form-item v-if="formModel.recipient_type === 'class'" path="class_ids" label="班级">
        <n-select
          v-model:value="formModel.class_ids"
          placeholder="请选择班级"
          multiple
          :options="classOptions"
          :loading="loadingClasses"
        />
      </n-form-item>
      
      <n-form-item v-if="formModel.recipient_type === 'user'" path="user_ids" label="用户">
        <n-select
          v-model:value="formModel.user_ids"
          placeholder="请选择用户"
          multiple
          filterable
          :options="userOptions"
          :loading="loadingUsers"
        />
      </n-form-item>
    </n-form>
    
    <template #footer>
      <div class="flex justify-end">
        <n-button @click="showModal = false" class="mr-2">取消</n-button>
        <n-button type="primary" :loading="submitting" @click="handleSubmit">
          发送
        </n-button>
      </div>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted } from 'vue';
import { 
  NModal, NForm, NFormItem, NInput, NRadioGroup, 
  NRadio, NSpace, NSelect, NButton, useMessage
} from 'naive-ui';
import { getClasses } from '@/services/api/classes';
import { getUsers } from '@/services/api/users';
import { createNotification } from '@/services/api/notifications';
import { useUserStore } from '@/stores/user';

interface FormModel {
  title: string;
  content: string;
  recipient_type: 'all' | 'class' | 'user';
  class_ids: number[];
  user_ids: number[];
}

interface ClassOption {
  label: string;
  value: number;
}

interface UserOption {
  label: string;
  value: number;
}

const props = defineProps<{
  show: boolean;
}>();

const emit = defineEmits<{
  (e: 'update:show', value: boolean): void;
  (e: 'success'): void;
}>();

const message = useMessage();
const userStore = useUserStore();
const formRef = ref<null | { validate: (callback: (errors?: any) => void) => void }>(null);
const showModal = computed({
  get: () => props.show,
  set: (value) => emit('update:show', value)
});

const formModel = reactive<FormModel>({
  title: '',
  content: '',
  recipient_type: 'all',
  class_ids: [],
  user_ids: []
});

const rules = {
  title: [
    { required: true, message: '请输入通知标题', trigger: 'blur' }
  ],
  content: [
    { required: true, message: '请输入通知内容', trigger: 'blur' }
  ],
  class_ids: [
    { 
      required: true, 
      type: 'array',
      message: '请选择至少一个班级', 
      trigger: 'change',
      validator: (_rule: any, value: number[]) => {
        return formModel.recipient_type !== 'class' || (value && value.length > 0);
      } 
    }
  ],
  user_ids: [
    { 
      required: true, 
      type: 'array',
      message: '请选择至少一个用户', 
      trigger: 'change',
      validator: (_rule: any, value: number[]) => {
        return formModel.recipient_type !== 'user' || (value && value.length > 0);
      } 
    }
  ]
};

const classOptions = ref<ClassOption[]>([]);
const userOptions = ref<UserOption[]>([]);
const loadingClasses = ref(false);
const loadingUsers = ref(false);
const submitting = ref(false);

onMounted(() => {
  fetchClasses();
});

watch(() => formModel.recipient_type, (newType) => {
  if (newType === 'user' && userOptions.value.length === 0) {
    fetchUsers();
  }
});

const fetchClasses = async () => {
  loadingClasses.value = true;
  try {
    const response = await getClasses();
    console.log('班级数据响应:', response);

    // 处理不同的响应格式
    let classesData = [];

    if (response?.data?.data && Array.isArray(response.data.data)) {
      // 标准的分页响应格式：{ data: { data: [...] } }
      classesData = response.data.data;
    } else if (response?.data && Array.isArray(response.data)) {
      // 直接数组响应：{ data: [...] }
      classesData = response.data;
    } else if (Array.isArray(response)) {
      // 直接是数组
      classesData = response;
    } else {
      console.error('未能识别的班级数据格式:', response);
      classesData = [];
    }

    // 转换为选项格式
    classOptions.value = classesData.map((cls: any) => ({
      label: cls.name,
      value: cls.id
    }));
  } catch (error) {
    console.error('Failed to fetch classes:', error);
    message.error('获取班级列表失败');
  } finally {
    loadingClasses.value = false;
  }
};

const fetchUsers = async () => {
  loadingUsers.value = true;
  try {
    const response = await getUsers();
    console.log('用户数据响应:', response);
    
    // 处理不同的响应格式
    let usersData = [];
    
    if (response?.data?.data && Array.isArray(response.data.data)) {
      // 标准的分页响应格式
      usersData = response.data.data;
    } else if (response?.data && Array.isArray(response.data)) {
      // 直接数组响应
      usersData = response.data;
    } else if (Array.isArray(response)) {
      // 直接是数组
      usersData = response;
    } else {
      console.error('未能识别的用户数据格式:', response);
      usersData = [];
    }
    
    // 转换为选项格式
    userOptions.value = usersData.map((user: any) => ({
      label: `${user.full_name || user.username} (${user.username})`,
      value: user.id
    }));
  } catch (error) {
    console.error('Failed to fetch users:', error);
    message.error('获取用户列表失败');
    userOptions.value = [];
  } finally {
    loadingUsers.value = false;
  }
};

const handleSubmit = () => {
  if (!formRef.value) return;
  
  // 将formRef.value保存到局部变量，防止后续操作中它被设为null
  const formRefLocal = formRef.value;
  
  formRefLocal.validate(async (errors) => {
    if (errors) return;
    
    submitting.value = true;
    
    try {
      const currentUser = userStore.user;
      
      if (!currentUser || !currentUser.id) {
        throw new Error('用户未登录或无法获取用户信息');
      }
      
      const payload = {
        title: formModel.title,
        content: formModel.content,
        notification_type: 'system',
        recipient_type: formModel.recipient_type,
        class_ids: formModel.recipient_type === 'class' ? formModel.class_ids : undefined,
        user_ids: formModel.recipient_type === 'user' ? formModel.user_ids : undefined,
        sender_id: currentUser.id
      };
      
      console.log('发送通知数据:', payload);
      
      // 等待通知创建完成
      await createNotification(payload);
      
      // 先恢复提交状态
      submitting.value = false;
      
      // 成功消息
      message.success('通知发送成功');
      
      // 先重置表单数据
      resetFormData();
      
      // 触发成功事件
      emit('success');
      
      // 延迟关闭模态框，确保所有状态正确更新
      setTimeout(() => {
        showModal.value = false;
      }, 0);
    } catch (error) {
      console.error('Failed to create notification:', error);
      message.error('通知发送失败');
      submitting.value = false;
    }
  });
};

// 仅重置表单数据，不涉及验证
const resetFormData = () => {
  formModel.title = '';
  formModel.content = '';
  formModel.recipient_type = 'all';
  formModel.class_ids = [];
  formModel.user_ids = [];
};

// 完整重置表单，包括验证状态
const resetForm = () => {
  // 先重置数据
  resetFormData();
  
  // 如果表单引用存在，重置验证状态
  // 包装在try-catch中，以防组件已卸载
  try {
    if (formRef.value) {
      formRef.value.validate((errors) => {
        // 这里可以忽略验证错误
      });
    }
  } catch (e) {
    console.warn('表单重置过程中出错，可能是组件已卸载', e);
  }
};
</script>
