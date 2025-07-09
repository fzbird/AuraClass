<template>
  <n-card class="dashboard-stat-card" hoverable>
    <div class="flex items-center">
      <div class="stat-icon-wrapper" :style="{ backgroundColor: bgColor }">
        <n-icon :size="24" class="text-white">
          <component :is="iconComponent" />
        </n-icon>
      </div>
      
      <div class="ml-4">
        <div class="text-gray-500 text-sm">{{ title }}</div>
        <div class="text-2xl font-bold mt-1">
          {{ value }}{{ suffix }}
        </div>
      </div>
    </div>
  </n-card>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { NCard, NIcon } from 'naive-ui';
import * as ionicons from '@vicons/ionicons5';

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  value: {
    type: [Number, String],
    required: true
  },
  icon: {
    type: String,
    required: true
  },
  color: {
    type: String,
    default: '#3366FF'
  },
  suffix: {
    type: String,
    default: ''
  }
});

const iconComponent = computed(() => {
  // 将 kebab-case 转换为 PascalCase 以匹配 ionicons 中的组件名
  const iconName = props.icon
    .split('-')
    .map(part => part.charAt(0).toUpperCase() + part.slice(1))
    .join('');
  
  return ionicons[iconName];
});

const bgColor = computed(() => {
  return props.color;
});
</script>

<style scoped>
.dashboard-stat-card {
  transition: transform 0.3s ease;
}

.dashboard-stat-card:hover {
  transform: translateY(-5px);
}

.stat-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
