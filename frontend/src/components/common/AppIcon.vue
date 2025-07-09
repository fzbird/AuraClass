<template>
  <n-icon
    :size="size"
    :color="color"
    :depth="depth"
    :component="icon"
    :style="style"
    :class="[className, iconClass]"
  >
    <slot v-if="!icon" />
  </n-icon>
</template>

<script setup lang="ts">
import { NIcon } from 'naive-ui';
import type { CSSProperties, Component, PropType } from 'vue';

const props = defineProps({
  // 图标大小
  size: {
    type: [String, Number],
    default: undefined
  },
  // 图标颜色
  color: {
    type: String,
    default: undefined
  },
  // 图标深度
  depth: {
    type: Number,
    default: undefined
  },
  // 图标组件
  icon: {
    type: Object as PropType<Component>,
    default: null
  },
  // 自定义样式
  style: {
    type: [String, Object] as unknown as PropType<string | CSSProperties>,
    default: () => ({})
  },
  // 自定义类名
  className: {
    type: String,
    default: ''
  },
  // 图标类名
  iconClass: {
    type: String,
    default: ''
  }
});
</script>

<style scoped>
/* 可根据需要添加自定义样式 */
</style> 