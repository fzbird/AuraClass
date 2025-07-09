<template>
  <div class="app-container">
    <n-config-provider :theme="themeStore.currentTheme" :theme-overrides="themeStore.themeOverrides">
      <n-loading-bar-provider>
        <n-dialog-provider>
          <n-notification-provider>
            <n-message-provider>
              <router-view />
            </n-message-provider>
          </n-notification-provider>
        </n-dialog-provider>
      </n-loading-bar-provider>
    </n-config-provider>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { 
  NConfigProvider, 
  NMessageProvider, 
  NDialogProvider, 
  NNotificationProvider,
  NLoadingBarProvider
} from 'naive-ui';
import { updateWsConfig } from './services/websocket/config';
import { useUserStore } from '@/stores/user';
import { usePermissionStore } from '@/stores/permission';
import { useThemeStore } from '@/stores/theme';

// 获取主题状态
const themeStore = useThemeStore();

// 在应用启动时确保WebSocket默认为禁用状态
onMounted(async () => {
  // 禁用WebSocket功能，直到用户在设置中手动启用
  updateWsConfig({ enabled: false });
  console.info('WebSocket功能默认禁用，可在系统设置中手动启用');

  const userStore = useUserStore();
  const permissionStore = usePermissionStore();
  // 如果本地存储有token，尝试恢复会话
  if (localStorage.getItem('token') && !userStore.user) {
    try {
      await userStore.fetchUserInfo();
      await permissionStore.loadPermissions();
      console.log('权限初始化完成');
    } catch (error) {
      console.error('权限初始化失败', error);
    }
  }
});
</script>

<style>
body {
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  background-color: #f5f7fa;
  color: #333;
  transition: background-color 0.3s ease, color 0.3s ease;
}

:root.dark body {
  background-color: #121212;
  color: #e5e5e5;
}

.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* Global scrollbar styles */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background-color: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
}

:root.dark ::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.2);
}

::-webkit-scrollbar-thumb:hover {
  background-color: rgba(0, 0, 0, 0.3);
}

:root.dark ::-webkit-scrollbar-thumb:hover {
  background-color: rgba(255, 255, 255, 0.3);
}
</style>
