<script setup lang="ts">
import { ref, reactive } from 'vue';
import { NForm, NFormItem, NInput, NButton, NDivider, NSwitch, NCard, useMessage } from 'naive-ui';
import http from '@/services/http';
import { useUserStore } from '@/stores/user';

const message = useMessage();
const userStore = useUserStore();

// 密码表单接口
interface PasswordForm {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

// 密码修改表单
const passwordFormRef = ref<any>(null);
const changingPassword = ref(false);

// 密码表单模型
const passwordModel = reactive<PasswordForm>({
  current_password: '',
  new_password: '',
  confirm_password: ''
});

// 密码表单验证规则
const passwordRules = {
  current_password: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 8, message: '密码长度不能少于8个字符', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule: any, value: string) => {
        return value === passwordModel.new_password;
      },
      message: '两次输入的密码不一致',
      trigger: 'blur'
    }
  ]
};

// 两因素认证状态
const twoFactorEnabled = ref(false);
const toggleTwoFactorLoading = ref(false);

// 实现密码更新功能
const handleChangePassword = () => {
  passwordFormRef.value?.validate(async (errors: any) => {
    if (errors) return;
    
    changingPassword.value = true;
    
    try {
      // 获取当前用户ID
      const userId = userStore.user?.id;
      if (!userId) {
        throw new Error('未找到用户ID');
      }
      
      // 调用更新密码的API - 使用users端点
      await http.put(`/users/${userId}`, {
        password: passwordModel.new_password,
        current_password: passwordModel.current_password
      });
      
      // 清空密码表单
      passwordModel.current_password = '';
      passwordModel.new_password = '';
      passwordModel.confirm_password = '';
      
      message.success('密码修改成功');
    } catch (error: any) {
      console.error('Failed to change password:', error);
      if (error.response?.status === 400 || error.response?.status === 401) {
        message.error('当前密码不正确');
      } else if (error.response?.status === 404) {
        message.error('用户不存在');
      } else {
        message.error('密码修改失败');
      }
    } finally {
      changingPassword.value = false;
    }
  });
};

// 处理两因素认证开关
const handleToggleTwoFactor = async (value: boolean) => {
  toggleTwoFactorLoading.value = true;
  
  try {
    // 这里替换为实际的两因素认证API调用
    // await http.put('/auth/two-factor', { enabled: value });
    message.success(value ? '两因素认证已启用' : '两因素认证已禁用');
  } catch (error) {
    console.error('Failed to toggle two-factor auth:', error);
    message.error('操作失败');
    // 如果失败，还原开关状态
    twoFactorEnabled.value = !value;
  } finally {
    toggleTwoFactorLoading.value = false;
  }
};
</script>

<template>
  <div class="account-security-settings">
    <NCard title="修改密码" class="password-card">
      <NForm
        ref="passwordFormRef"
        :model="passwordModel"
        :rules="passwordRules"
        label-placement="left"
        label-width="100"
      >
        <NFormItem path="current_password" label="当前密码">
          <NInput
            v-model:value="passwordModel.current_password"
            type="password"
            placeholder="输入当前密码"
            show-password-on="click"
          />
        </NFormItem>
        
        <NFormItem path="new_password" label="新密码">
          <NInput
            v-model:value="passwordModel.new_password"
            type="password"
            placeholder="输入新密码"
            show-password-on="click"
          />
        </NFormItem>
        
        <NFormItem path="confirm_password" label="确认密码">
          <NInput
            v-model:value="passwordModel.confirm_password"
            type="password"
            placeholder="再次输入新密码"
            show-password-on="click"
          />
        </NFormItem>
        
        <NFormItem>
          <NButton type="primary" @click="handleChangePassword" :loading="changingPassword">
            更新密码
          </NButton>
        </NFormItem>
      </NForm>
    </NCard>
    
    <NDivider />
    
    <NCard title="两因素认证" class="two-factor-card">
      <div class="two-factor-auth">
        <div class="setting-row">
          <span>启用两因素认证</span>
          <NSwitch 
            v-model:value="twoFactorEnabled" 
            :loading="toggleTwoFactorLoading"
            @update:value="handleToggleTwoFactor"
          />
        </div>
        <p class="tip">启用两因素认证后，每次登录时都需要输入额外的验证码</p>
      </div>
    </NCard>
  </div>
</template>

<style scoped>
.account-security-settings {
  max-width: 600px;
}

.password-card,
.two-factor-card {
  margin-bottom: 20px;
}

.setting-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.tip {
  font-size: 12px;
  color: #888;
  margin-top: 8px;
}

.two-factor-auth {
  margin-top: 0;
}
</style> 