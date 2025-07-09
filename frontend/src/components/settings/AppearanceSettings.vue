<script setup lang="ts">
import { ref } from 'vue';
import { NSelect, NFormItem, NSwitch, NDivider, NSpace, NButton } from 'naive-ui';
import { useAppStore } from '@/stores/app';

const appStore = useAppStore();

// 主题设置
const themeOptions = [
  { label: '跟随系统', value: 'system' },
  { label: '浅色模式', value: 'light' },
  { label: '深色模式', value: 'dark' }
];

const selectedTheme = ref(appStore.theme || 'system');
const handleThemeChange = (value: string) => {
  selectedTheme.value = value;
  if (value === 'dark') {
    appStore.enableDarkMode();
  } else if (value === 'light') {
    appStore.disableDarkMode();
  } else {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    if (prefersDark) {
      appStore.enableDarkMode();
    } else {
      appStore.disableDarkMode();
    }
  }
};

// 界面密度设置
const densityOptions = [
  { label: '默认', value: 'default' },
  { label: '紧凑', value: 'compact' },
  { label: '舒适', value: 'comfortable' }
];
const selectedDensity = ref('default');

// 重置设置
const handleResetSettings = () => {
  selectedTheme.value = 'system';
  selectedDensity.value = 'default';
  appStore.resetUISettings();
};
</script>

<template>
  <div class="appearance-settings">
    <div class="setting-section">
      <h3>主题设置</h3>
      <NFormItem label="界面主题">
        <NSelect 
          v-model:value="selectedTheme" 
          :options="themeOptions"
          @update:value="handleThemeChange" 
        />
      </NFormItem>
      
      <div class="setting-row">
        <span>动画效果</span>
        <NSwitch v-model:value="appStore.enableAnimations" />
      </div>
    </div>
    
    <NDivider />
    
    <div class="setting-section">
      <h3>界面设置</h3>
      <NFormItem label="界面密度">
        <NSelect v-model:value="selectedDensity" :options="densityOptions" />
      </NFormItem>
    </div>
    
    <NDivider />
    
    <div class="setting-actions">
      <NSpace>
        <NButton type="primary" @click="appStore.saveUISettings">保存设置</NButton>
        <NButton @click="handleResetSettings">重置设置</NButton>
      </NSpace>
    </div>
  </div>
</template>

<style scoped>
.setting-section {
  margin-bottom: 24px;
}

h3 {
  margin-bottom: 16px;
  font-weight: 500;
  color: #333;
}

.setting-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.setting-actions {
  margin-top: 24px;
}
</style> 