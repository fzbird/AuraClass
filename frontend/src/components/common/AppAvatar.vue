<template>
  <n-avatar
    :src="src"
    :size="size"
    :round="round"
    :circle="circle"
    :color="color"
    :style="style"
    :class="[className, avatarClass]"
    :bordered="bordered"
    :object-fit="objectFit"
    :fallback-src="fallbackSrc"
    :on-error="onError"
  >
    <template #default v-if="$slots.default">
      <slot />
    </template>
    <template #fallback v-if="$slots.fallback">
      <slot name="fallback" />
    </template>
    <template v-if="!$slots.default && !$slots.fallback && fallbackText">
      {{ computedText }}
    </template>
  </n-avatar>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { NAvatar } from 'naive-ui';
import type { CSSProperties, PropType } from 'vue';

type AvatarSize = 'small' | 'medium' | 'large' | number;
type ObjectFit = 'fill' | 'contain' | 'cover' | 'none' | 'scale-down';

const props = defineProps({
  // 头像图片地址
  src: {
    type: String,
    default: ''
  },
  // 头像大小
  size: {
    type: [String, Number] as PropType<AvatarSize>,
    default: 'medium'
  },
  // 是否圆角
  round: {
    type: Boolean,
    default: false
  },
  // 是否圆形
  circle: {
    type: Boolean,
    default: true
  },
  // 背景颜色
  color: {
    type: String,
    default: undefined
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
  // 头像组件类名
  avatarClass: {
    type: String,
    default: ''
  },
  // 是否有边框
  bordered: {
    type: Boolean,
    default: false
  },
  // 图片适应方式
  objectFit: {
    type: String as () => ObjectFit,
    default: 'cover'
  },
  // 后备图片地址
  fallbackSrc: {
    type: String,
    default: ''
  },
  // 错误处理函数
  onError: {
    type: Function as PropType<(e: Event) => void>,
    default: undefined
  },
  // 无图片时显示的文字
  fallbackText: {
    type: String,
    default: ''
  },
  // 文字显示长度
  textLength: {
    type: Number,
    default: 1
  }
});

// 计算后的显示文字
const computedText = computed(() => {
  if (!props.fallbackText) return '';
  return props.fallbackText.substring(0, props.textLength).toUpperCase();
});
</script>

<style scoped>
/* 可根据需要添加自定义样式 */
</style> 