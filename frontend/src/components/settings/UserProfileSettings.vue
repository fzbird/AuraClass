<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { 
  NForm, NFormItem, NInput, NButton, NSpace, 
  NAvatar, NUpload, NIcon, NSpin, useMessage,
  NCard, type FormInst
} from 'naive-ui';
import { useUserStore } from '@/stores/user';
import http from '@/services/http';

// 扩展用户类型以包含所需字段
interface UserProfile {
  username: string;
  full_name: string;
  email: string;
  phone: string;
  avatar: string;
  [key: string]: any;
}

const props = defineProps({
  onUpdate: {
    type: Function,
    default: () => {}
  }
});

const userStore = useUserStore();
const message = useMessage();
// 使用any类型来避免类型检查错误
const formRef = ref<any>(null);
const loading = ref(false);
const submitting = ref(false);
const defaultAvatarUrl = '/assets/default-avatar.png';

// 创建默认值以防止undefined
const userDefaults: UserProfile = {
  username: '',
  full_name: '',
  email: '',
  phone: '',
  avatar: ''
};

// 将store中的用户数据与默认值合并
const user = userStore.user || {};
const userData = { ...userDefaults, ...user };

const formModel = reactive<UserProfile>({
  username: userData.username || '',
  full_name: userData.full_name || '',
  email: userData.email || '',
  phone: userData.phone || '',
  avatar: userData.avatar || ''
});

const rules = {
  full_name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }
  ]
};

onMounted(() => {
  initFormData();
});

const initFormData = () => {
  if (userStore.user) {
    formModel.username = userData.username || '';
    formModel.full_name = userData.full_name || '';
    formModel.email = userData.email || '';
    formModel.phone = userData.phone || '';
    formModel.avatar = userData.avatar || '';
  }
};

const handleAvatarUpload = async (options: any) => {
  const { file } = options;
  if (!file) return;
  
  try {
    const formData = new FormData();
    formData.append('file', file.file as File);
    formData.append('module', 'profile');
    formData.append('entity_type', 'avatar');
    formData.append('entity_id', String(userStore.user?.id || '0'));
    formData.append('upload_id', String(userStore.user?.id || '0'));
    formData.append('is_public', '1');
    
    console.log("正在上传文件:", file.file);
    
    const response = await http.post('/uploads', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    
    console.log('上传成功，原始响应:', response);
    const responseData = response.data || response;
    console.log('处理后的响应数据:', responseData);
    
    // 获取头像URL，处理多种可能的响应结构
    const extractAvatarUrl = (data: any): string | null => {
      if (!data) return null;
      
      // 直接在顶层查找
      if (data.file_url) return data.file_url;
      if (data.avatar_url) return data.avatar_url;
      if (data.url) return data.url;
      
      // 检查data.data嵌套结构
      if (data.data) {
        if (typeof data.data === 'object') {
          if (data.data.file_url) return data.data.file_url;
          if (data.data.avatar_url) return data.data.avatar_url;
          if (data.data.url) return data.data.url;
        }
      }
      
      // 检查数组结构
      if (Array.isArray(data)) {
        const firstItem = data[0];
        if (firstItem && typeof firstItem === 'object') {
          if (firstItem.file_url) return firstItem.file_url;
          if (firstItem.avatar_url) return firstItem.avatar_url;
          if (firstItem.url) return firstItem.url;
        }
      }
      
      return null;
    };
    
    const avatarUrl = extractAvatarUrl(responseData);
    
    if (avatarUrl) {
      formModel.avatar = avatarUrl;
      if (options.onFinish) {
        options.onFinish();
      }
      message.success('头像上传成功');
    } else {
      console.error('未找到有效的头像URL，API响应:', responseData);
      throw new Error('未收到有效的头像URL');
    }
  } catch (error) {
    console.error('Failed to upload avatar:', error);
    if (options.onError) {
      options.onError();
    }
    message.error('头像上传失败');
  }
};

const handleSubmit = () => {
  formRef.value?.validate(async (errors: any) => {
    if (errors) return;
    
    submitting.value = true;
    
    try {
      const userData = {
        full_name: formModel.full_name,
        email: formModel.email,
        phone: formModel.phone,
        avatar: formModel.avatar
      };
      
      // 更新用户资料
      await http.put('/auth/me', userData);
      
      // 调用父组件的更新方法
      if (props.onUpdate) {
        props.onUpdate(userData);
      }
      
      // 刷新当前用户信息
      await userStore.fetchUserInfo();
      
      message.success('个人信息更新成功');
    } catch (error) {
      console.error('Failed to update profile:', error);
      message.error('个人信息更新失败');
    } finally {
      submitting.value = false;
    }
  });
};
</script>

<template>
  <div class="user-profile-settings">
    <NSpin :show="loading">
      <NCard title="基本信息" class="profile-card">
        <NForm
          ref="formRef"
          :model="formModel"
          :rules="rules"
          label-placement="left"
          label-width="100"
        >
          <NFormItem path="username" label="用户名">
            <NInput v-model:value="formModel.username" disabled />
          </NFormItem>
          
          <NFormItem path="full_name" label="姓名">
            <NInput v-model:value="formModel.full_name" placeholder="输入姓名" />
          </NFormItem>
          
          <NFormItem path="email" label="邮箱">
            <NInput v-model:value="formModel.email" placeholder="输入邮箱" />
          </NFormItem>
          
          <NFormItem path="phone" label="手机号">
            <NInput v-model:value="formModel.phone" placeholder="输入手机号" />
          </NFormItem>
          
          <NFormItem path="avatar" label="头像">
            <div class="avatar-upload">
              <NAvatar
                :src="formModel.avatar || undefined"
                :fallback-src="defaultAvatarUrl"
                size="large"
                round
                class="avatar-preview"
              />
              <NUpload
                :custom-request="handleAvatarUpload"
                :show-file-list="false"
                accept="image/*"
              >
                <NButton>更换头像</NButton>
              </NUpload>
            </div>
          </NFormItem>
          
          <NFormItem>
            <NButton type="primary" @click="handleSubmit" :loading="submitting">
              保存修改
            </NButton>
          </NFormItem>
        </NForm>
      </NCard>
    </NSpin>
  </div>
</template>

<style scoped>
.user-profile-settings {
  max-width: 600px;
}

.profile-card {
  margin-bottom: 20px;
}

.avatar-upload {
  display: flex;
  align-items: center;
  gap: 16px;
}

.avatar-preview {
  width: 64px;
  height: 64px;
  border-radius: 50% !important; /* 强制使用圆形 */
  object-fit: cover;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

:deep(.n-avatar) {
  border-radius: 50% !important;
}

:deep(.n-avatar__img) {
  border-radius: 50% !important;
}
</style> 