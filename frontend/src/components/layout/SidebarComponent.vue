<template>
  <div class="sidebar"
       :class="{ 
         'sidebar-collapsed': !isExpanded,
         'dark-theme': isDarkMode
       }">
    <div class="sidebar-content">
      <n-menu 
        :options="menuOptions" 
        :value="activeKey" 
        :collapsed="!isExpanded"
        @update:value="handleMenuClick" 
        :collapsed-width="64"
        :indent="18"
        class="sidebar-menu" 
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, h } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { NMenu } from 'naive-ui';
import { renderIcon } from '@/utils/icons';
import { usePermissionStore } from '@/stores/permission';
import { useAppStore } from '@/stores/app';
import { useThemeStore } from '@/stores/theme';

const route = useRoute();
const router = useRouter();
const permissionStore = usePermissionStore();
const appStore = useAppStore();
const themeStore = useThemeStore();

const isExpanded = computed(() => appStore.isSidebarExpanded);
const activeKey = computed(() => route.name as string);
const isDarkMode = computed(() => themeStore.darkMode);

// Handle menu item click
const handleMenuClick = (key: string) => {
  // 使用try-catch包裹路由导航，防止组件卸载后的错误
  try {
    if (key && key !== activeKey.value) {
      router.push({ name: key }).catch(err => {
        console.error('Navigation error:', err);
      });
    }
  } catch (error) {
    console.error('Menu navigation error:', error);
  }
};

// 检查是否显示菜单项
const shouldShowMenuItem = (permission: string) => {
  return !permission || permissionStore.hasPermission(permission);
};

// 菜单配置
const menuOptions = computed(() => {
  const options = [
    {
      label: '仪表盘',
      key: 'Dashboard',
      icon: renderIcon('HomeOutline'),
      show: true
    },
    {
      label: '学生管理',
      key: 'Students',
      icon: renderIcon('PeopleOutline'),
      show: shouldShowMenuItem('view:students')
    },
    {
      label: '量化项目',
      key: 'QuantItems',
      icon: renderIcon('ListOutline'),
      show: shouldShowMenuItem('view:quant-items')
    },
    {
      label: '量化记录',
      key: 'Records',
      icon: renderIcon('DocumentTextOutline'),
      show: shouldShowMenuItem('view:records')
    },
    {
      label: '统计分析',
      key: 'Statistics',
      icon: renderIcon('BarChartOutline'),
      show: shouldShowMenuItem('view:statistics')
    },
    {
      label: '通知管理',
      key: 'Notifications',
      icon: renderIcon('NotificationsOutline'),
      show: shouldShowMenuItem('view:notifications')
    },
    {
      label: 'AI 助手',
      key: 'AIAssistant',
      icon: renderIcon('BulbOutline'),
      show: shouldShowMenuItem('use:ai-assistant')
    },
    {
      label: '系统设置',
      key: 'Settings',
      icon: renderIcon('SettingsOutline'),
      show: shouldShowMenuItem('view:settings')
    }
  ];
  
  return options.filter(option => option.show);
});
</script>

<style>
.sidebar {
  width: 220px;
  height: 100%;
  background-color: #ffffff;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1), background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
  position: fixed;
  left: 0;
  top: 60px;
  z-index: 40;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  border-right: 1px solid #e5e7eb;
}

.sidebar.dark-theme {
  background-color: #1a1a1a;
  border-right: 1px solid #333;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
  color: #e5e5e5;
}

.sidebar.sidebar-expanded {
  width: 220px;
}

.sidebar:not(.sidebar-expanded) {
  width: 64px;
}

.sidebar-content {
  height: 100%;
  overflow-y: auto;
  overflow-x: hidden;
  scrollbar-width: thin;
}

.sidebar-content::-webkit-scrollbar {
  width: 4px;
}

.sidebar-content::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar-content::-webkit-scrollbar-thumb {
  background-color: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
}

.dark-theme .sidebar-content::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.2);
}

.sidebar-menu {
  padding: 8px 0;
}

.sidebar-icon {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 8px;
  color: inherit;
}

.sidebar-icon svg {
  width: 100%;
  height: 100%;
}

.sidebar:not(.sidebar-expanded) .sidebar-icon {
  margin-right: 0;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 10px 16px;
  color: #4b5563;
  text-decoration: none;
  transition: all 0.2s;
  border-left: 3px solid transparent;
}

.dark-theme .menu-item {
  color: #e5e5e5;
}

.menu-item:hover {
  background-color: rgba(0, 0, 0, 0.03);
}

.dark-theme .menu-item:hover {
  background-color: rgba(255, 255, 255, 0.05);
}

.menu-item.active {
  color: #4f46e5;
  background-color: rgba(79, 70, 229, 0.05);
  border-left-color: #4f46e5;
}

.dark-theme .menu-item.active {
  color: #6366f1;
  background-color: rgba(99, 102, 241, 0.15);
}

.menu-icon {
  flex-shrink: 0;
  margin-right: 12px;
}

.menu-title {
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 折叠侧边栏时的样式 */
.sidebar:not(.sidebar-expanded) .menu-title {
  display: none;
}

.sidebar:not(.sidebar-expanded) .menu-item {
  justify-content: center;
  padding: 10px 0;
}

.sidebar:not(.sidebar-expanded) .menu-icon {
  margin-right: 0;
}

.menu-group {
  margin-bottom: 4px;
}

.menu-group-title {
  font-size: 12px;
  color: #6b7280;
  padding: 8px 16px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.dark-theme .menu-group-title {
  color: #9ca3af;
}

/* 折叠时隐藏分组标题 */
.sidebar:not(.sidebar-expanded) .menu-group-title {
  display: none;
}
</style>
