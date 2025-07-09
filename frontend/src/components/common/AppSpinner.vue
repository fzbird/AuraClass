<template>
  <div :class="['app-spinner-wrapper', className, wrapperClass]" :style="wrapperStyle">
    <n-spin
      :size="size"
      :show="show"
      :stroke="stroke"
      :stroke-width="strokeWidth"
      :rotate="rotate"
      :description="description"
      :style="style"
      :class="spinnerClass"
    >
      <template v-if="$slots.default">
        <div :class="['app-spinner-content', contentClass]" :style="contentStyle">
          <slot />
        </div>
      </template>
      <template #icon v-if="$slots.icon">
        <slot name="icon" />
      </template>
      <template #description v-if="$slots.description">
        <slot name="description" />
      </template>
    </n-spin>
  </div>
</template>

<script setup lang="ts">
import { NSpin } from 'naive-ui';
import type { CSSProperties, PropType } from 'vue';

type SpinnerSize = 'small' | 'medium' | 'large' | number;

const props = defineProps({
  // 加载器大小
  size: {
    type: [String, Number] as PropType<SpinnerSize>,
    default: 'medium'
  },
  // 是否显示
  show: {
    type: Boolean,
    default: true
  },
  // 线条颜色
  stroke: {
    type: String,
    default: undefined
  },
  // 线条宽度
  strokeWidth: {
    type: Number,
    default: undefined
  },
  // 旋转角度
  rotate: {
    type: Boolean,
    default: true
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
  // 外层容器样式
  wrapperStyle: {
    type: [String, Object] as unknown as PropType<string | CSSProperties>,
    default: () => ({})
  },
  // 内容区域样式
  contentStyle: {
    type: [String, Object] as unknown as PropType<string | CSSProperties>,
    default: () => ({})
  },
  // 自定义类名
  className: {
    type: String,
    default: ''
  },
  // 加载器类名
  spinnerClass: {
    type: String,
    default: ''
  },
  // 容器类名
  wrapperClass: {
    type: String,
    default: ''
  },
  // 内容区域类名
  contentClass: {
    type: String,
    default: ''
  }
});
</script>

<style scoped>
.app-spinner-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.app-spinner-content {
  width: 100%;
  height: 100%;
}
</style>
