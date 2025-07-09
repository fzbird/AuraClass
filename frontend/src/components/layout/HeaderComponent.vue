<template>
  <header class="header">
    <div class="header-container">
      <!-- 左侧 Logo 和菜单折叠按钮 -->
      <div class="header-left">
        <button class="menu-toggle" @click="toggleSidebar" aria-label="Toggle sidebar">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="3" y1="12" x2="21" y2="12"></line>
            <line x1="3" y1="6" x2="21" y2="6"></line>
            <line x1="3" y1="18" x2="21" y2="18"></line>
          </svg>
        </button>
        
        <router-link to="/" class="logo">
          <span class="logo-text">AuraClass</span>
        </router-link>
      </div>
      
      <!-- 右侧用户菜单和通知 -->
      <div class="header-right">
        <!-- AI助手 -->
        <AIAssistant class="hidden sm:block" />

        <!-- 主题切换 -->
        <div class="theme-toggle">
          <n-dropdown :options="themeOptions" trigger="click" @select="handleThemeSelect">
            <button class="theme-toggle-btn" aria-label="Toggle theme">
              <!-- 深色模式图标 -->
              <svg v-if="themeStore.mode === 'dark'" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
              </svg>
              <!-- 浅色模式图标 -->
              <svg v-else-if="themeStore.mode === 'light'" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="5"></circle>
                <line x1="12" y1="1" x2="12" y2="3"></line>
                <line x1="12" y1="21" x2="12" y2="23"></line>
                <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
                <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
                <line x1="1" y1="12" x2="3" y2="12"></line>
                <line x1="21" y1="12" x2="23" y2="12"></line>
                <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
                <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
              </svg>
              <!-- 系统模式图标 -->
              <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect>
                <line x1="8" y1="21" x2="16" y2="21"></line>
                <line x1="12" y1="17" x2="12" y2="21"></line>
              </svg>
            </button>
          </n-dropdown>
        </div>
        
        <!-- 通知图标 -->
        <notification-icon />
        
        <!-- 用户下拉菜单 -->
        <n-dropdown :options="userMenuOptions" @select="handleUserMenuSelect" trigger="click">
          <div class="user-menu">
            <n-avatar round size="small" :fallback-src="avatarFallback">
              {{ user?.full_name?.charAt(0) || 'U' }}
            </n-avatar>
            <span class="user-name">{{ user?.full_name }}</span>
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="hidden sm:inline-block">
              <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
          </div>
        </n-dropdown>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { NAvatar, NDropdown } from 'naive-ui';
import { useUserStore } from '@/stores/user';
import { useAppStore } from '@/stores/app';
import { useThemeStore } from '@/stores/theme';
import NotificationIcon from './NotificationIcon.vue';
import AIAssistant from '@/components/assistant/AIAssistant.vue';

const router = useRouter();
const userStore = useUserStore();
const appStore = useAppStore();
const themeStore = useThemeStore();

const user = computed(() => userStore.user);
const avatarFallback = ref('/assets/default-avatar.png');

const themeOptions = [
  {
    label: '浅色主题',
    key: 'light'
  },
  {
    label: '深色主题',
    key: 'dark'
  },
  {
    label: '跟随系统',
    key: 'system'
  }
];

const handleThemeSelect = (key: string) => {
  themeStore.setThemeMode(key as 'light' | 'dark' | 'system');
};

const userMenuOptions = [
  {
    label: '个人设置',
    key: 'settings'
  },
  {
    label: '退出登录',
    key: 'logout'
  }
];

const handleUserMenuSelect = (key: string) => {
  switch (key) {
    case 'settings':
      router.push('/settings');
      break;
    case 'logout':
      userStore.logout();
      router.push('/auth/login');
      break;
  }
};

const toggleSidebar = () => {
  appStore.toggleSidebar();
};
</script>

<style scoped>
.header {
  background-color: #ffffff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  z-index: 50;
  transition: background-color 0.3s ease, box-shadow 0.3s ease;
  padding: 0;
  margin: 0;
  width: 100%;
}

:root.dark .header {
  background-color: #1a1a1a;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.header-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 0;
  height: 60px;
  box-sizing: border-box;
}

.header-left {
  display: flex;
  align-items: center;
  padding: 0;
  margin: 0;
}

.menu-toggle {
  margin: 0;
  padding: 8px 16px;
  border-radius: 0;
  line-height: 0;
  color: #4b5563;
  transition: background-color 0.2s, color 0.3s;
  box-sizing: border-box;
}

:root.dark .menu-toggle {
  color: #e5e5e5;
}

.menu-toggle:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

:root.dark .menu-toggle:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.logo {
  display: flex;
  align-items: center;
  text-decoration: none;
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
  color: #4f46e5;
  transition: color 0.3s;
  margin-left: 4px;
}

:root.dark .logo-text {
  color: #6366f1;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-right: 16px;
}

.theme-toggle-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  line-height: 0;
  color: #4b5563;
  transition: background-color 0.2s, color 0.3s;
}

:root.dark .theme-toggle-btn {
  color: #e5e5e5;
}

.theme-toggle-btn:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

:root.dark .theme-toggle-btn:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.user-menu:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

:root.dark .user-menu:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.user-name {
  margin-left: 8px;
  font-size: 14px;
  color: #374151;
  display: none;
  transition: color 0.3s;
}

:root.dark .user-name {
  color: #e5e5e5;
}

@media (min-width: 640px) {
  .user-name {
    display: block;
  }
  
  .hidden {
    display: none;
  }
  
  .sm\:block,
  .sm\:inline-block {
    display: block;
  }
}
</style>
