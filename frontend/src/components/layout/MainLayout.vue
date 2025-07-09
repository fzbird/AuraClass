<template>
  <div class="main-layout">
    <n-loading-bar-provider>
      <n-message-provider>
        <header-component />
        
        <div class="main-container">
          <sidebar-component :class="{ 'sidebar-expanded': isSidebarExpanded }" />
          
          <div class="content-area" :class="{ 'sidebar-expanded': isSidebarExpanded }">
            <breadcrumbs-component class="hidden md:block" />
            
            <page-container>
              <router-view v-slot="{ Component }">
                <transition name="fade" mode="out-in">
                  <keep-alive>
                    <div class="route-component-wrapper">
                      <component 
                        :is="Component"
                        :key="$route.fullPath" />
                    </div>
                  </keep-alive>
                </transition>
              </router-view>
            </page-container>
            
            <footer-component />
          </div>
        </div>
        
        <!-- 移动端导航菜单，小屏幕下显示 -->
        <mobile-menu class="md:hidden" />
        
        <!-- 离线状态指示器 -->
        <offline-indicator />
      </n-message-provider>
    </n-loading-bar-provider>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, watch } from 'vue';
import { NLoadingBarProvider, NMessageProvider } from 'naive-ui';
import HeaderComponent from './HeaderComponent.vue';
import SidebarComponent from './SidebarComponent.vue';
import BreadcrumbsComponent from './BreadcrumbsComponent.vue';
import PageContainer from './PageContainer.vue';
import FooterComponent from './FooterComponent.vue';
import MobileMenu from './MobileMenu.vue';
import OfflineIndicator from './OfflineIndicator.vue';
import { useAppStore } from '@/stores/app';
import { useThemeStore } from '@/stores/theme';
import { useBreakpoints } from '@/utils/responsive';

const appStore = useAppStore();
const themeStore = useThemeStore();
const { isMobile, smallerThan } = useBreakpoints();

// 提供sidebar状态
const isSidebarExpanded = computed(() => appStore.isSidebarExpanded);

// 计算是否为深色模式
const isDarkMode = computed(() => themeStore.darkMode);

// 监听主题变化，更新布局样式
watch(isDarkMode, (newValue) => {
  const layoutElement = document.querySelector('.main-layout');
  if (layoutElement) {
    if (newValue) {
      layoutElement.classList.add('dark-theme');
    } else {
      layoutElement.classList.remove('dark-theme');
    }
  }
}, { immediate: true });

// 初始化应用状态
onMounted(() => {
  appStore.initAppearance();
  
  // 监听窗口大小变化，在小屏幕上自动折叠侧边栏
  const handleResize = () => {
    if (smallerThan('md').value && appStore.isSidebarExpanded) {
      appStore.toggleSidebar();
    }
  };
  
  // 初始检查
  handleResize();
  
  window.addEventListener('resize', handleResize);
  
  // 初始应用主题
  if (isDarkMode.value) {
    document.querySelector('.main-layout')?.classList.add('dark-theme');
  }
  
  return () => {
    window.removeEventListener('resize', handleResize);
  };
});
</script>

<style scoped>
.main-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f9fafb;
  transition: background-color 0.3s ease, color 0.3s ease;
}

.main-layout.dark-theme {
  background-color: #121212;
  color: #e5e5e5;
}

.main-container {
  display: flex;
  flex: 1;
  position: relative;
  min-height: calc(100vh - 60px); /* 减去header高度 */
}

.content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  overflow-x: hidden;
  transition: margin-left 0.3s ease, background-color 0.3s ease;
  background-color: #f9fafb;
  padding: 16px;
  min-height: calc(100vh - 60px);
  width: 100%;
  max-width: 1280px;
  margin: 0 auto;
}

.dark-theme .content-area {
  background-color: #121212;
}

/* 响应式样式 */
@media (min-width: 768px) {
  .content-area {
    padding: 24px;
  }
  
  .content-area.sidebar-expanded {
    margin-left: 220px; /* 保持与sidebar宽度匹配 */
    width: calc(100% - 220px);
  }
  
  .content-area:not(.sidebar-expanded) {
    margin-left: 64px; /* 保持与折叠sidebar宽度匹配 */
    width: calc(100% - 64px);
  }
}

/* 页面过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 工具类 */
.hidden {
  display: none;
}

@media (min-width: 768px) {
  .md\:block {
    display: block;
  }
  
  .md\:hidden {
    display: none;
  }
}

/* 路由组件包装器 */
.route-component-wrapper {
  height: 100%;
  width: 100%;
}
</style>
