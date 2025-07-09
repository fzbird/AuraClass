<template>
  <div class="auth-layout">
    <n-message-provider>
      <div class="auth-container">
        <div class="auth-left">
          <div class="system-intro">
            <h1 class="system-name">AuraClass</h1>
            <h2 class="system-slogan">班级量化管理系统</h2>
            <p class="system-description">提升班级管理效率，激发学生潜能</p>
          </div>
        </div>
        
        <div class="auth-right">
          <div class="login-panel">
            <div class="login-header">
              <h2 class="login-title">用户登录</h2>
              <p class="login-subtitle">欢迎回来，请登录您的账号</p>
            </div>
            
            <n-form
              ref="formRef"
              :model="formModel"
              :rules="rules"
              label-placement="top"
              @submit.prevent="handleSubmit"
              class="login-form"
            >
              <n-form-item path="username" label="用户名">
                <n-input
                  v-model:value="formModel.username"
                  placeholder="请输入用户名"
                >
                  <template #prefix>
                    <n-icon><UserOutlined /></n-icon>
                  </template>
                </n-input>
              </n-form-item>
              
              <n-form-item path="password" label="密码">
                <n-input
                  v-model:value="formModel.password"
                  type="password"
                  placeholder="请输入密码"
                  show-password-on="click"
                >
                  <template #prefix>
                    <n-icon><LockOutlined /></n-icon>
                  </template>
                </n-input>
              </n-form-item>
              
              <div class="login-options">
                <n-checkbox v-model:checked="rememberMe">
                  记住我
                </n-checkbox>
                
                <a href="#" class="forgot-password">忘记密码?</a>
              </div>
              
              <n-button
                type="primary"
                block
                :loading="loading"
                attr-type="submit"
                class="login-button"
                color="#19be6b"
              >
                登录
              </n-button>
            </n-form>
            
          </div>
        </div>
      </div>
    
    <div class="auth-footer">
      <p>© {{ currentYear }} AuraClass. All rights reserved.</p>
    </div>
    </n-message-provider>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { 
  NForm, 
  NFormItem, 
  NInput, 
  NButton, 
  NCheckbox, 
  NIcon,
  useMessage,
  NMessageProvider
} from 'naive-ui';
import { 
  UserOutlined, 
  LockOutlined 
} from '@vicons/antd';
import { useUserStore } from '@/stores/user';

const router = useRouter();
const route = useRoute();
const userStore = useUserStore();
const message = useMessage();

const formRef = ref<typeof NForm | null>(null);
const loading = ref(false);
const rememberMe = ref(false);
const devMode = ref(true); // 开发模式标志
const currentYear = computed(() => new Date().getFullYear());

const formModel = reactive({
  username: '',
  password: ''
});

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不少于6个字符', trigger: 'blur' }
  ]
};

// 添加全局键盘事件处理函数
const handleKeyDown = (e: KeyboardEvent) => {
  // 当按下回车键且不在输入过程中时触发登录
  if (e.key === 'Enter' && !loading.value) {
    handleSubmit(e);
  }
};

const handleSubmit = (e: Event) => {
  e.preventDefault();
  formRef.value?.validate(async (errors: Array<any> | undefined) => {
    if (errors) return;
    
    loading.value = true;
    try {
      await userStore.login({
        username: formModel.username,
        password: formModel.password
      });
      
      message.success('登录成功');
      
      // 存储用户名，如果选择了"记住我"
      if (rememberMe.value) {
        localStorage.setItem('rememberedUsername', formModel.username);
      } else {
        localStorage.removeItem('rememberedUsername');
      }
      
      // 重定向到之前的页面或仪表盘
      const redirectPath = route.query.redirect as string || '/dashboard';
      // 确保重定向路径不是登录页或者不包含redirect参数循环
      if (redirectPath.includes('/auth/login') || redirectPath.includes('redirect=')) {
        router.push('/dashboard');
      } else {
        router.push(redirectPath);
      }
    } catch (error: any) {
      message.error(error.message || '登录失败，请检查用户名和密码');
    } finally {
      loading.value = false;
    }
  });
};

// 初始化表单，如果存在记住的用户名
onMounted(() => {
  const rememberedUsername = localStorage.getItem('rememberedUsername');
  if (rememberedUsername) {
    formModel.username = rememberedUsername;
    rememberMe.value = true;
  }
  
  // 在开发环境中使用默认账户密码
  if (import.meta.env.DEV && !rememberedUsername) {
    formModel.username = 'admin';
    formModel.password = 'admin123';
  }
  
  // 添加全局键盘事件监听
  document.addEventListener('keydown', handleKeyDown);
});

// 组件销毁时移除事件监听，防止内存泄漏
onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyDown);
});
</script>

<style scoped>
.auth-layout {
  display: flex;
  flex-direction: column;
  min-height: 70vh;
  width: 100%;
  background-color: #fff;
  position: relative;
  padding-bottom: 60px; /* 添加底部填充，避免内容被footer遮挡 */
}

.auth-container {
  flex: 1;
  display: flex;
  width: 100%;
  max-width: 1000px;
  max-height: 600px; 
  margin: auto;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  overflow: hidden;
}

.auth-left {
  width: 50%;
  background-color: #3366FF;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.system-intro {
  text-align: center;
}

.system-name {
  font-size: 3.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
  line-height: 1.2;
}

.system-slogan {
  font-size: 1.8rem;
  font-weight: 600;
  margin-bottom: 2rem;
}

.system-description {
  font-size: 1.1rem;
  line-height: 1.6;
}

.auth-right {
  width: 50%;
  background: white;
  padding: 2rem;
  display: flex;
  flex-direction: column;
}

.login-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 1rem;
}

.login-form {
  width: 100%;
}

.n-form-item {
  margin-bottom: 1.2rem;
}

/* 添加输入框样式修复 */
:deep(.n-input) {
  width: 100%;
  background-color: white;
}

:deep(.n-input__input-el) {
  height: 38px;
  padding: 0 12px;
  line-height: 38px;
  color: #333;
  background-color: white;
}

:deep(.n-input__border),
:deep(.n-input__state-border) {
  background-color: transparent;
}

:deep(.n-input--focus) {
  border-color: #3366FF;
}

.login-header {
  margin-bottom: 1.5rem;
  text-align: center;
}

.login-title {
  font-size: 1.8rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 0.5rem;
}

.login-subtitle {
  color: #666;
  font-size: 0.95rem;
}

.login-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 0.5rem 0 1.2rem;
}

.forgot-password {
  color: #3366FF;
  font-size: 0.9rem;
  text-decoration: none;
}

.login-button {
  height: 44px;
  font-size: 1rem;
}

.demo-mode-info {
  margin-top: 1rem;
  display: flex;
  justify-content: center;
}

.demo-mode-button {
  font-size: 0.9rem;
  padding: 0.3rem 1rem;
  background-color: #f0f7ff;
  border-radius: 4px;
}

.auth-footer {
  bottom: 0;
  left: 0;
  right: 0;
  text-align: center;
  color: #999;
  font-size: 0.8rem;
  padding: 1rem;
  background-color: #fff;
  display: flex;
  justify-content: center;
  align-items: center;
}

.auth-footer p {
  max-width: 900px;
  width: 100%;
  margin: 0 auto;
}

/* 响应式调整 */
@media screen and (max-width: 768px) {
  .auth-container {
    flex-direction: column;
    height: auto;
    max-width: 500px;
  }
  
  .auth-left, .auth-right {
    width: 100%;
  }
  
  .auth-left {
    padding: 2rem 1rem;
  }
  
  .system-name {
    font-size: 2.5rem;
  }
  
  .system-slogan {
    font-size: 1.5rem;
    margin-bottom: 1rem;
  }
}

@media screen and (max-width: 576px) {
  .auth-container {
    box-shadow: none;
    border-radius: 0;
  }
  
  .system-name {
    font-size: 2rem;
  }
  
  .system-slogan {
    font-size: 1.2rem;
  }
}

/* 优化表单项和标签样式 */
:deep(.n-form-item) {
  display: flex;
  flex-direction: column;
  margin-bottom: 20px;
}

:deep(.n-form-item-label) {
  height: auto;
  padding-bottom: 6px;
  font-size: 14px;
  color: #333;
}

:deep(.n-form-item-blank) {
  min-height: 40px;
}

/* 密码字段图标样式 */
:deep(.n-input__eye) {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
}

:deep(.n-input__eye:hover) {
  color: #3366FF;
}

/* 确保输入框内容区域背景色正确 */
:deep(.n-input__input-wrapper) {
  background-color: white !important;
}

:deep(.n-input-wrapper) {
  background-color: white !important;
}
</style>
