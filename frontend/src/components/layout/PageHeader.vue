<script setup lang="ts">
import { useBreakpoints } from '@/utils/responsive';

// 定义组件属性
defineProps({
  title: {
    type: String,
    required: true
  },
  subtitle: {
    type: String,
    default: ''
  }
});

// 导出响应式断点信息，可在模板中使用
const { isMobile } = useBreakpoints();
</script>

<template>
  <div class="page-header" :class="{ 'with-actions': $slots.actions }">
    <div class="page-header-content">
      <h1 class="page-title">{{ title }}</h1>
      <p v-if="subtitle" class="page-subtitle">{{ subtitle }}</p>
    </div>
    <div v-if="$slots.actions" class="page-actions">
      <slot name="actions"></slot>
    </div>
  </div>
</template>

<style scoped>
.page-header {
  margin-bottom: 24px;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.page-header-content {
  flex: 1;
  min-width: 0;
}

.page-title {
  margin: 0;
  font-size: 1.75rem;
  font-weight: 600;
  line-height: 1.4;
  color: var(--text-color-primary, #333);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.page-subtitle {
  margin: 4px 0 0 0;
  font-size: 1rem;
  color: var(--text-color-secondary, #666);
  line-height: 1.5;
}

.page-actions {
  display: flex;
  gap: 8px;
  align-items: center;
  justify-content: flex-end;
}

/* 响应式样式 */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .page-header-content,
  .page-actions {
    width: 100%;
  }
  
  .page-title {
    font-size: 1.5rem;
  }
  
  .page-subtitle {
    font-size: 0.875rem;
  }
  
  .page-actions {
    justify-content: flex-start;
  }
  
  .with-actions .page-header-content {
    margin-bottom: 8px;
  }
}
</style> 