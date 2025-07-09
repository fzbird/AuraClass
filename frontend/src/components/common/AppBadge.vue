<template>
  <n-badge
    :show="show"
    :value="value"
    :max="max"
    :dot="dot"
    :type="type"
    :color="color"
    :processing="processing"
    :show-zero="showZero"
    :offset="offset"
    :style="style"
    :class="[className, badgeClass]"
    :position="position"
  >
    <slot />
  </n-badge>
</template>

<script setup lang="ts">
import { NBadge } from 'naive-ui';
import type { CSSProperties, PropType } from 'vue';

type BadgeType = 'default' | 'error' | 'info' | 'success' | 'warning';
type BadgePosition =
  | 'top-right'
  | 'top-left'
  | 'bottom-right'
  | 'bottom-left';

const props = defineProps({
  // 是否显示徽章
  show: {
    type: Boolean,
    default: true
  },
  // 徽章内容
  value: {
    type: [Number, String],
    default: null
  },
  // 最大值
  max: {
    type: Number,
    default: 99
  },
  // 是否为小圆点
  dot: {
    type: Boolean,
    default: false
  },
  // 徽章类型
  type: {
    type: String as () => BadgeType,
    default: 'default'
  },
  // 自定义颜色
  color: {
    type: String,
    default: undefined
  },
  // 是否显示动画
  processing: {
    type: Boolean,
    default: false
  },
  // 值为0时是否显示
  showZero: {
    type: Boolean,
    default: false
  },
  // 偏移量
  offset: {
    type: Array as unknown as PropType<[number, number]>,
    default: () => [0, 0]
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
  // 徽章类名
  badgeClass: {
    type: String,
    default: ''
  },
  // 徽章位置
  position: {
    type: String as () => BadgePosition,
    default: 'top-right'
  }
});
</script>

<style scoped>
/* 可根据需要添加自定义样式 */
</style> 