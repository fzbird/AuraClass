<template>
  <n-card
    :title="title"
    :content-style="contentStyle"
    :bordered="bordered"
    :size="size"
    :hoverable="hoverable"
    :segment="segment"
    :shadow="shadow"
    :style="cardStyle"
    :class="[className, cardClass]"
    :footer-style="footerStyle"
    :header-style="headerStyle"
    :header-extra-style="headerExtraStyle"
    :embedded="embedded"
    :closable="closable"
    @close="handleClose"
  >
    <template #header-extra v-if="$slots['header-extra']">
      <slot name="header-extra" />
    </template>
    <template #cover v-if="$slots.cover">
      <slot name="cover" />
    </template>
    <template #header v-if="$slots.header">
      <slot name="header" />
    </template>
    <template #default>
      <slot />
    </template>
    <template #footer v-if="$slots.footer">
      <slot name="footer" />
    </template>
    <template #action v-if="$slots.action">
      <slot name="action" />
    </template>
  </n-card>
</template>

<script setup lang="ts">
import { NCard } from 'naive-ui';
import type { CSSProperties } from 'vue';

const props = defineProps({
  // 卡片标题
  title: {
    type: String,
    default: ''
  },
  // 是否显示边框
  bordered: {
    type: Boolean,
    default: true
  },
  // 卡片尺寸
  size: {
    type: String,
    default: 'medium',
    validator: (val: string) => ['small', 'medium', 'large', 'huge'].includes(val)
  },
  // 是否在悬浮时展示阴影
  hoverable: {
    type: Boolean,
    default: false
  },
  // 分段控制
  segment: {
    type: [String, Array] as unknown as () => 'top' | 'bottom' | 'left' | 'right' | Array<'top' | 'bottom' | 'left' | 'right'>,
    default: null
  },
  // 是否显示阴影
  shadow: {
    type: Boolean,
    default: false
  },
  // 内容区域样式
  contentStyle: {
    type: [String, Object] as unknown as () => string | CSSProperties,
    default: () => ({})
  },
  // 页脚样式
  footerStyle: {
    type: [String, Object] as unknown as () => string | CSSProperties,
    default: () => ({})
  },
  // 头部样式
  headerStyle: {
    type: [String, Object] as unknown as () => string | CSSProperties,
    default: () => ({})
  },
  // 头部额外内容样式
  headerExtraStyle: {
    type: [String, Object] as unknown as () => string | CSSProperties,
    default: () => ({})
  },
  // 内嵌模式
  embedded: {
    type: Boolean,
    default: false
  },
  // 是否可关闭
  closable: {
    type: Boolean,
    default: false
  },
  // 自定义样式
  cardStyle: {
    type: [String, Object] as unknown as () => string | CSSProperties,
    default: () => ({})
  },
  // 自定义类名
  className: {
    type: String,
    default: ''
  },
  // 额外的卡片类名
  cardClass: {
    type: String,
    default: ''
  }
});

const emit = defineEmits(['close']);

const handleClose = (e: MouseEvent) => {
  emit('close', e);
};
</script>

<style scoped>
/* 可根据需要添加自定义样式 */
</style>
