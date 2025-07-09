import { defineStore } from 'pinia';
import { ref, computed, watch } from 'vue';
import { darkTheme, lightTheme } from 'naive-ui';
import type { GlobalTheme } from 'naive-ui';

/**
 * 主题类型
 */
export type ThemeMode = 'light' | 'dark' | 'system';

/**
 * 主题状态
 */
export interface ThemeState {
  mode: ThemeMode;
  darkMode: boolean;
  themeOverrides: Record<string, any>;
}

/**
 * 系统颜色方案变化媒体查询
 */
const systemDarkMode = window.matchMedia('(prefers-color-scheme: dark)');

/**
 * 主题状态管理
 */
export const useThemeStore = defineStore('theme', () => {
  // 主题模式: light, dark, system
  const mode = ref<ThemeMode>(
    (localStorage.getItem('auraclass_theme_mode') as ThemeMode) || 'system'
  );
  
  // 是否深色模式
  const darkMode = ref(false);
  
  // 主题定制配置
  const themeOverrides = ref<Record<string, any>>({
    common: {
      primaryColor: '#2080f0',
      primaryColorHover: '#4098fc',
      primaryColorPressed: '#1060c9',
      infoColor: '#2080f0',
      successColor: '#18a058',
      warningColor: '#f0a020',
      errorColor: '#d03050'
    }
  });
  
  // 计算当前主题
  const currentTheme = computed<GlobalTheme>(() => {
    return darkMode.value ? darkTheme : lightTheme;
  });

  // 初始化主题
  const initTheme = () => {
    // 根据主题模式判断是否启用深色模式
    if (mode.value === 'dark') {
      darkMode.value = true;
    } else if (mode.value === 'light') {
      darkMode.value = false;
    } else {
      // 系统模式下，根据系统偏好设置
      darkMode.value = systemDarkMode.matches;
    }
    
    // 应用深色模式到HTML根元素
    applyDarkMode();
  };
  
  // 设置主题模式
  const setThemeMode = (newMode: ThemeMode) => {
    mode.value = newMode;
    
    // 保存到本地存储
    localStorage.setItem('auraclass_theme_mode', newMode);
    
    // 更新深色模式
    if (newMode === 'dark') {
      darkMode.value = true;
    } else if (newMode === 'light') {
      darkMode.value = false;
    } else {
      darkMode.value = systemDarkMode.matches;
    }
  };
  
  // 设置深色模式
  const setDarkMode = (isDark: boolean) => {
    darkMode.value = isDark;
    
    // 如果当前是系统模式，则切换到明确的模式
    if (mode.value === 'system') {
      mode.value = isDark ? 'dark' : 'light';
      localStorage.setItem('auraclass_theme_mode', mode.value);
    }
  };
  
  // 更新主题配置
  const updateThemeOverrides = (overrides: Record<string, any>) => {
    themeOverrides.value = {
      ...themeOverrides.value,
      ...overrides
    };
  };
  
  // 应用深色模式到HTML根元素
  const applyDarkMode = () => {
    // 为HTML根元素添加/移除'dark'类
    if (darkMode.value) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  };
  
  // 监听深色模式变化
  watch(darkMode, () => {
    applyDarkMode();
  });
  
  // 监听系统颜色方案变化
  systemDarkMode.addEventListener('change', (e) => {
    if (mode.value === 'system') {
      darkMode.value = e.matches;
    }
  });
  
  // 初始化主题
  initTheme();
  
  return {
    mode,
    darkMode,
    themeOverrides,
    currentTheme,
    setThemeMode,
    setDarkMode,
    updateThemeOverrides
  };
}); 