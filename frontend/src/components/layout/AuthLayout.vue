<template>
  <div class="auth-layout">
    <div class="auth-container">
      <div class="auth-card">        
        <div class="auth-content">
          <n-message-provider>
            <router-view />
          </n-message-provider>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { NMessageProvider } from 'naive-ui';
// 认证布局组件
</script>

<style scoped>
.auth-layout {
  display: flex;
  min-height: 100vh;
  background-color: #f9fafb;
}

.auth-container {
  display: flex;
  flex-direction: column;
  justify-content: center; /* 垂直居中 */
  align-items: center; /* 水平居中 */
  width: 100%;
  padding: 2rem 1rem;
}

.auth-card {
  width: 100%;
}

.auth-content {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

.text-primary {
  color: #3366FF;
}
</style>