<template>
  <n-alert
    :title="title"
    :type="type"
    :closable="closable"
    :show-icon="showIcon"
    :bordered="bordered"
    :size="size"
    :description="description"
    :style="style"
    :class="[className, alertClass]"
    :on-after-leave="onAfterLeave"
    @close="handleClose"
  >
    <template #icon v-if="$slots.icon">
      <slot name="icon" />
    </template>

    <template #header v-if="$slots.header">
      <slot name="header" />
    </template>

    <template #default v-if="$slots.default">
      <slot />
    </template>

    <template #footer v-if="$slots.footer">
      <slot name="footer" />
    </template>

    <template #action v-if="$slots.action">
      <slot name="action" />
    </template>
  </n-alert>
</template>

<script setup lang="ts">
import { NAlert } from 'naive-ui';
import type { CSSProperties, PropType } from 'vue';

type AlertType = 'default' | 'info' | 'success' | 'warning' | 'error';
type AlertSize = 'small' | 'medium' | 'large';

const props = defineProps({
  // 标题
  title: {
    type: String,
    default: ''
  },
  // 提示类型
  type: {
    type: String as () => AlertType,
    default: 'default'
  },
  // 是否可关闭
  closable: {
    type: Boolean,
    default: false
  },
  // 是否显示图标
  showIcon: {
    type: Boolean,
    default: true
  },
  // 是否有边框
  bordered: {
    type: Boolean,
    default: true
  },
  // 提示框大小
  size: {
    type: String as () => AlertSize,
    default: 'medium'
  },
  // 描述文本
  description: {
    type: String,
    default: ''
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
  // 提示框类名
  alertClass: {
    type: String,
    default: ''
  },
  // 关闭动画结束后的回调
  onAfterLeave: {
    type: Function as PropType<() => void>,
    default: undefined
  }
});

const emit = defineEmits(['close', 'after-leave']);

// 处理关闭事件
const handleClose = (e: MouseEvent) => {
  emit('close', e);
};
</script>

<style scoped>
/* 可根据需要添加自定义样式 */
</style> 