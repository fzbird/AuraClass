<template>
  <div class="responsive-container" :class="containerClasses">
    <slot></slot>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useBreakpoints } from '@/utils/responsive';

// 组件属性
const props = defineProps({
  // 是否铺满容器高度
  fullHeight: {
    type: Boolean,
    default: false
  },
  // 自动调整内容间距
  adaptiveSpacing: {
    type: Boolean,
    default: true
  },
  // 移动端下是否居中内容
  centerOnMobile: {
    type: Boolean,
    default: false
  },
  // 最大宽度
  maxWidth: {
    type: String,
    default: ''
  },
  // 填充模式
  padding: {
    type: String,
    default: 'normal' // 'none', 'small', 'normal', 'large'
  }
});

// 使用响应式断点
const { isMobile, isTablet, smallerThan, currentBreakpoint } = useBreakpoints();

// 计算容器类
const containerClasses = computed(() => {
  return {
    'full-height': props.fullHeight,
    'adaptive-spacing': props.adaptiveSpacing,
    'center-on-mobile': props.centerOnMobile && isMobile(),
    [`padding-${props.padding}`]: true,
    [`breakpoint-${currentBreakpoint.value}`]: true
  };
});

// 根据屏幕大小导出布局相关值，可用于子组件
const layoutInfo = computed(() => {
  return {
    isMobile: isMobile(),
    isTablet: isTablet(),
    isCompact: smallerThan('lg'),
    breakpoint: currentBreakpoint.value
  };
});

// 暴露布局信息给父组件
defineExpose({
  layoutInfo
});
</script>

<style scoped>
.responsive-container {
  width: 100%;
  margin: 0 auto;
  transition: padding 0.3s ease;
}

.full-height {
  height: 100%;
}

/* 最大宽度 */
.responsive-container[style*="max-width"] {
  width: 100%;
}

/* 填充模式 */
.padding-none {
  padding: 0;
}

.padding-small {
  padding: 8px;
}

.padding-normal {
  padding: 16px;
}

.padding-large {
  padding: 24px;
}

/* 响应式适配不同屏幕大小 */
.breakpoint-xs.adaptive-spacing {
  padding: 8px;
}

.breakpoint-sm.adaptive-spacing {
  padding: 12px;
}

.breakpoint-md.adaptive-spacing {
  padding: 16px;
}

.breakpoint-lg.adaptive-spacing,
.breakpoint-xl.adaptive-spacing,
.breakpoint-xxl.adaptive-spacing {
  padding: 24px;
}

/* 移动端居中 */
.center-on-mobile {
  display: flex;
  flex-direction: column;
  align-items: center;
}
</style> 