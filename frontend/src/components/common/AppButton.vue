<template>
  <n-button
    :type="type"
    :size="size"
    :disabled="disabled"
    :loading="loading"
    :circle="circle"
    :color="color"
    :text="text"
    :tag="tag"
    :ghost="ghost"
    :round="round"
    :quaternary="quaternary"
    :dashed="dashed"
    :block="block"
    :focusable="focusable"
    :keyboard="keyboard"
    :strong="strong"
    :secondary="secondary"
    :tertiary="tertiary"
    :class="[className, buttonClass]"
    :style="style"
    :render-icon="renderIcon"
    :theme="theme"
    @click="handleClick"
  >
    <template #icon v-if="$slots.icon">
      <slot name="icon" />
    </template>
    <slot />
  </n-button>
</template>

<script setup lang="ts">
import { NButton } from 'naive-ui';
import type { CSSProperties, PropType } from 'vue';

type ButtonType = 'default' | 'tertiary' | 'primary' | 'info' | 'success' | 'warning' | 'error';
type ButtonSize = 'tiny' | 'small' | 'medium' | 'large';

const props = defineProps({
  // 按钮类型
  type: {
    type: String as () => ButtonType,
    default: 'default'
  },
  // 按钮大小
  size: {
    type: String as () => ButtonSize,
    default: 'medium'
  },
  // 是否禁用
  disabled: {
    type: Boolean,
    default: false
  },
  // 是否加载中
  loading: {
    type: Boolean,
    default: false
  },
  // 是否为圆形按钮
  circle: {
    type: Boolean,
    default: false
  },
  // 按钮颜色
  color: {
    type: String,
    default: undefined
  },
  // 是否为文本按钮
  text: {
    type: Boolean,
    default: false
  },
  // 按钮标签
  tag: {
    type: String,
    default: 'button'
  },
  // 是否为幽灵按钮
  ghost: {
    type: Boolean,
    default: false
  },
  // 是否为圆角按钮
  round: {
    type: Boolean,
    default: false
  },
  // 是否为四级按钮
  quaternary: {
    type: Boolean,
    default: false
  },
  // 是否为虚线按钮
  dashed: {
    type: Boolean,
    default: false
  },
  // 是否为块级按钮
  block: {
    type: Boolean,
    default: false
  },
  // 是否可聚焦
  focusable: {
    type: Boolean,
    default: true
  },
  // 是否支持键盘操作
  keyboard: {
    type: Boolean,
    default: true
  },
  // 是否为加粗按钮
  strong: {
    type: Boolean,
    default: false
  },
  // 是否为次要按钮
  secondary: {
    type: Boolean,
    default: false
  },
  // 是否为第三按钮
  tertiary: {
    type: Boolean,
    default: false
  },
  // 自定义图标渲染函数
  renderIcon: {
    type: Function,
    default: undefined
  },
  // 自定义主题
  theme: {
    type: Object,
    default: undefined
  },
  // 自定义类名
  className: {
    type: String,
    default: ''
  },
  // 按钮类名
  buttonClass: {
    type: String,
    default: ''
  },
  // 自定义样式
  style: {
    type: [String, Object] as unknown as PropType<string | CSSProperties>,
    default: () => ({})
  }
});

const emit = defineEmits(['click']);

// 处理点击事件
const handleClick = (e: MouseEvent) => {
  if (!props.disabled && !props.loading) {
    emit('click', e);
  }
};
</script>

<style scoped>
/* 可根据需要添加自定义样式 */
</style>
