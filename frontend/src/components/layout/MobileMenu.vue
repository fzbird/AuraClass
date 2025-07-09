<template>
  <div class="mobile-menu">
    <n-drawer
      v-model:show="showDrawer"
      :width="280"
      placement="left"
      :trap-focus="false"
      display-directive="show"
    >
      <n-drawer-content title="菜单导航">
        <div class="drawer-content">
          <!-- 用户信息 -->
          <div class="user-profile">
            <n-avatar
              size="large"
              round
              :src="userAvatar"
              :fallback-src="defaultAvatar"
            />
            <div class="user-info">
              <div class="user-name">{{ userName }}</div>
              <div class="user-role">{{ userRole }}</div>
            </div>
          </div>
          
          <n-divider />
          
          <!-- 主菜单 -->
          <n-menu
            v-model:value="activeKey"
            :options="menuOptions"
            :accordion="true"
            :indent="12"
            @update:value="handleMenuClick"
          />
          
          <n-divider />
          
          <!-- 底部菜单项 -->
          <div class="bottom-menu">
            <n-space vertical>
              <!-- 离线模式开关 -->
              <div class="menu-item">
                <n-space align="center" justify="space-between">
                  <div class="menu-item-label">
                    <n-icon size="18" class="menu-item-icon">
                      <component :is="isOnline ? 'WifiOutlined' : 'DisconnectOutlined'" />
                    </n-icon>
                    <span>离线模式</span>
                  </div>
                  <n-switch 
                    v-model:value="offlineModeEnabled" 
                    @update:value="toggleOfflineMode"
                    size="small"
                  />
                </n-space>
              </div>
              
              <!-- 深色模式开关 -->
              <div class="menu-item">
                <n-space align="center" justify="space-between">
                  <div class="menu-item-label">
                    <n-icon size="18" class="menu-item-icon">
                      <component :is="isDarkMode ? 'BulbOutlined' : 'BulbFilled'" />
                    </n-icon>
                    <span>深色模式</span>
                  </div>
                  <n-switch 
                    v-model:value="darkMode" 
                    @update:value="toggleDarkMode"
                    size="small"
                  />
                </n-space>
              </div>
              
              <!-- 退出按钮 -->
              <div class="menu-item logout">
                <n-button block @click="handleLogout">
                  <template #icon>
                    <n-icon><logout-outlined /></n-icon>
                  </template>
                  退出登录
                </n-button>
              </div>
            </n-space>
          </div>
        </div>
      </n-drawer-content>
    </n-drawer>
    
    <!-- 移动端底部导航栏 -->
    <div class="mobile-tabs">
      <div 
        v-for="item in bottomTabs" 
        :key="item.key"
        class="tab-item"
        :class="{ active: activeKey === item.key }"
        @click="() => handleTabClick(item)"
      >
        <n-icon size="20">
          <component :is="item.icon" />
        </n-icon>
        <div class="tab-label">{{ item.label }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, h } from 'vue';
import { useRouter } from 'vue-router';
import { 
  NDrawer, 
  NDrawerContent, 
  NMenu, 
  NDivider, 
  NAvatar,
  NIcon,
  NButton,
  NSpace,
  NSwitch,
  useMessage 
} from 'naive-ui';
import type { MenuOption } from 'naive-ui';
import { useUserStore } from '@/stores/user';
import { useThemeStore } from '@/stores/theme';
import { useNetworkStatus, isOnline, offlineEnabled } from '@/utils/offline';
import DashboardOutlined from '@vicons/antd/es/DashboardOutlined';
import TeamOutlined from '@vicons/antd/es/TeamOutlined';
import BookOutlined from '@vicons/antd/es/BookOutlined';
import BarChartOutlined from '@vicons/antd/es/BarChartOutlined';
import SettingOutlined from '@vicons/antd/es/SettingOutlined';
import MenuOutlined from '@vicons/antd/es/MenuOutlined';
import WifiOutlined from '@vicons/antd/es/WifiOutlined';
import DisconnectOutlined from '@vicons/antd/es/DisconnectOutlined';
import BulbOutlined from '@vicons/antd/es/BulbOutlined';
import BulbFilled from '@vicons/antd/es/BulbFilled';
import LogoutOutlined from '@vicons/antd/es/LogoutOutlined';
import defaultAvatarImg from "/assets/user-avatar.png";

// 组件属性
const props = defineProps({
  showDrawer: {
    type: Boolean,
    default: false
  }
});

// 组件事件
const emit = defineEmits(['update:showDrawer', 'logout']);

// 计算菜单显示状态
const showDrawer = computed({
  get: () => props.showDrawer,
  set: (value) => emit('update:showDrawer', value)
});

// 路由
const router = useRouter();
const userStore = useUserStore();
const themeStore = useThemeStore();
const message = useMessage();
const { toggleOfflineMode } = useNetworkStatus();

// 当前激活的菜单项
const activeKey = ref<string | null>(null);

// 默认头像
const defaultAvatar = defaultAvatarImg;

// 用户信息
const userName = computed(() => userStore.user?.full_name || '未登录');
const userAvatar = computed(() => ''); // 用户模型没有avatar属性，使用默认值
const userRole = computed(() => {
  const roleMap: Record<string, string> = {
    'admin': '管理员',
    'teacher': '教师',
    'assistant': '助教'
  };
  const roleId = userStore.user?.role_id || 0;
  const roleName = roleId === 1 ? 'admin' : roleId === 2 ? 'teacher' : 'assistant';
  return roleMap[roleName] || '未知角色';
});

// 深色模式
const isDarkMode = computed(() => themeStore.darkMode);
const darkMode = computed({
  get: () => themeStore.darkMode,
  set: (value) => themeStore.setDarkMode(value)
});

// 离线模式
const offlineModeEnabled = computed({
  get: () => offlineEnabled.value,
  set: (value) => toggleOfflineMode(value)
});

// 渲染图标
const renderIcon = (icon: any) => {
  return () => h(NIcon, null, { default: () => h(icon) });
};

// 主菜单选项
const menuOptions = computed<MenuOption[]>(() => [
  {
    label: '控制台',
    key: 'dashboard',
    icon: renderIcon(DashboardOutlined),
  },
  {
    label: '班级管理',
    key: 'classes',
    icon: renderIcon(TeamOutlined),
    children: [
      {
        label: '班级列表',
        key: 'classes/list'
      },
      {
        label: '班级成员',
        key: 'classes/members'
      }
    ]
  },
  {
    label: '学生管理',
    key: 'students',
    icon: renderIcon(TeamOutlined)
  },
  {
    label: '量化管理',
    key: 'quant-management',
    icon: renderIcon(BookOutlined),
    children: [
      {
        label: '量化项目',
        key: 'quant-items'
      },
      {
        label: '量化记录',
        key: 'records'
      },
      {
        label: '批量记录',
        key: 'batch-records'
      }
    ]
  },
  {
    label: '数据统计',
    key: 'statistics',
    icon: renderIcon(BarChartOutlined),
    children: [
      {
        label: '综合统计',
        key: 'statistics/overview'
      },
      {
        label: '班级统计',
        key: 'statistics/classes'
      },
      {
        label: '趋势分析',
        key: 'statistics/trends'
      }
    ]
  },
  {
    label: 'AI助手',
    key: 'ai-assistant',
    icon: renderIcon(BulbOutlined)
  },
  {
    label: '系统设置',
    key: 'settings',
    icon: renderIcon(SettingOutlined),
    children: [
      {
        label: '个人设置',
        key: 'settings/profile'
      },
      {
        label: '系统参数',
        key: 'settings/system'
      }
    ]
  }
]);

// 底部导航栏选项
const bottomTabs = [
  {
    key: 'dashboard',
    label: '首页',
    icon: DashboardOutlined,
    path: '/dashboard'
  },
  {
    key: 'students',
    label: '学生',
    icon: TeamOutlined,
    path: '/students'
  },
  {
    key: 'records',
    label: '记录',
    icon: BookOutlined,
    path: '/records'
  },
  {
    key: 'more',
    label: '更多',
    icon: MenuOutlined,
    action: () => showDrawer.value = true
  }
];

// 处理菜单点击
const handleMenuClick = (key: string) => {
  // 关闭抽屉
  showDrawer.value = false;
  
  // 路由映射
  const routeMap: Record<string, string> = {
    'dashboard': '/dashboard',
    'classes': '/classes',
    'classes/list': '/classes',
    'classes/members': '/classes/members',
    'students': '/students',
    'quant-items': '/quant-items',
    'records': '/records',
    'batch-records': '/records/batch',
    'statistics/overview': '/statistics',
    'statistics/classes': '/statistics/classes',
    'statistics/trends': '/statistics/trends',
    'ai-assistant': '/ai-assistant',
    'settings/profile': '/settings/profile',
    'settings/system': '/settings/system'
  };
  
  // 如果有对应的路由，则导航到该路由
  const path = routeMap[key];
  if (path) {
    router.push(path);
  }
};

// 处理底部Tab点击
const handleTabClick = (item: typeof bottomTabs[0]) => {
  if (item.key === 'more') {
    if (item.action) {
      item.action();
    }
  } else {
    activeKey.value = item.key;
    
    if (item.path) {
      router.push(item.path);
    }
  }
};

// 切换深色模式
const toggleDarkMode = (value: boolean) => {
  themeStore.setDarkMode(value);
};

// 处理退出
const handleLogout = async () => {
  try {
    await userStore.logout();
    emit('logout');
    showDrawer.value = false;
    router.push('/login');
    message.success('已成功退出登录');
  } catch (error) {
    console.error('Logout error:', error);
    message.error('退出登录失败，请重试');
  }
};
</script>

<style scoped>
.drawer-content {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.user-profile {
  display: flex;
  align-items: center;
  padding: 12px 16px;
}

.user-info {
  margin-left: 12px;
}

.user-name {
  font-weight: 500;
  font-size: 16px;
}

.user-role {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.bottom-menu {
  margin-top: auto;
  padding: 16px;
}

.menu-item {
  padding: 8px 0;
}

.menu-item-label {
  display: flex;
  align-items: center;
}

.menu-item-icon {
  margin-right: 8px;
}

.logout {
  margin-top: 12px;
}

.mobile-tabs {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  background-color: var(--n-color, #fff);
  border-top: 1px solid var(--n-border-color, #f0f0f0);
  z-index: 100;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.05);
}

.tab-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 8px 0;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-item.active {
  color: var(--n-primary-color, #2080f0);
}

.tab-label {
  font-size: 12px;
  margin-top: 4px;
}
</style> 