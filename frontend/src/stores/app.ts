import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export interface AppearanceSettings {
  theme_mode: 'light' | 'dark' | 'system';
  primary_color: string;
  layout_mode: 'sidebar' | 'topbar';
  content_width: 'fluid' | 'fixed';
  font_size: 'small' | 'medium' | 'large';
  enable_animations: boolean;
  show_breadcrumbs: boolean;
  compact_mode: boolean;
}

export const useAppStore = defineStore('app', () => {
  const appearance = ref<AppearanceSettings>({
    theme_mode: 'light',
    primary_color: '#3366FF',
    layout_mode: 'sidebar',
    content_width: 'fluid',
    font_size: 'medium',
    enable_animations: true,
    show_breadcrumbs: true,
    compact_mode: false
  });
  
  // 侧边栏状态
  const isSidebarExpanded = ref(true);
  const isFullscreen = ref(false);
  
  // 通过 localStorage 初始化设置
  const initAppearance = () => {
    const savedAppearance = localStorage.getItem('appearance');
    if (savedAppearance) {
      appearance.value = JSON.parse(savedAppearance);
    }
    
    // 检查系统主题偏好
    if (appearance.value.theme_mode === 'system') {
      const prefersDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
      appearance.value.theme_mode = prefersDarkMode ? 'dark' : 'light';
    }
    
    // 恢复侧边栏状态
    const savedSidebarState = localStorage.getItem('sidebar_expanded');
    if (savedSidebarState !== null) {
      isSidebarExpanded.value = savedSidebarState === 'true';
    }
    
    // 应用主题设置
    applyThemeSettings();
  };
  
  // 更新界面设置
  const updateAppearance = async (settings: AppearanceSettings) => {
    appearance.value = settings;
    
    // 保存到本地存储
    localStorage.setItem('appearance', JSON.stringify(settings));
    
    // 应用主题设置
    applyThemeSettings();
  };
  
  // 应用主题设置到文档
  const applyThemeSettings = () => {
    // 应用主题模式
    document.documentElement.setAttribute('data-theme', appearance.value.theme_mode);
    
    // 应用主色调
    document.documentElement.style.setProperty('--primary-color', appearance.value.primary_color);
    
    // 应用字体大小
    const fontSizeMap = {
      'small': '14px',
      'medium': '16px',
      'large': '18px'
    };
    document.documentElement.style.setProperty('--base-font-size', fontSizeMap[appearance.value.font_size]);
    
    // 应用紧凑模式
    if (appearance.value.compact_mode) {
      document.documentElement.classList.add('compact-mode');
    } else {
      document.documentElement.classList.remove('compact-mode');
    }
    
    // 应用动画效果
    if (!appearance.value.enable_animations) {
      document.documentElement.classList.add('disable-animations');
    } else {
      document.documentElement.classList.remove('disable-animations');
    }
  };
  
  // 切换侧边栏展开/收起状态
  const toggleSidebar = () => {
    isSidebarExpanded.value = !isSidebarExpanded.value;
    localStorage.setItem('sidebar_expanded', isSidebarExpanded.value.toString());
  };
  
  // 切换全屏模式
  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
      isFullscreen.value = true;
    } else if (document.exitFullscreen) {
      document.exitFullscreen();
      isFullscreen.value = false;
    }
  };
  
  // 全局加载状态
  const isLoading = ref(false);
  
  // 全局通知状态
  const notification = ref({
    show: false,
    type: 'info',
    message: '',
    duration: 3000
  });
  
  // 显示通知
  const showNotification = (
    message: string,
    type: 'success' | 'info' | 'warning' | 'error' = 'info',
    duration: number = 3000
  ) => {
    notification.value = {
      show: true,
      type,
      message,
      duration
    };
    
    setTimeout(() => {
      notification.value.show = false;
    }, duration);
  };
  
  // 计算当前是否为暗色模式
  const isDarkMode = computed(() => appearance.value.theme_mode === 'dark');
  
  return {
    appearance,
    isSidebarExpanded,
    isFullscreen,
    isDarkMode,
    initAppearance,
    updateAppearance,
    toggleSidebar,
    toggleFullscreen,
    isLoading,
    notification,
    showNotification
  };
});
