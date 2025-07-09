<template>
  <div :class="[className, inputClass]" :style="style">
    <n-input-number
      :value="value"
      :min="min"
      :max="max"
      :step="step"
      :precision="precision"
      :placeholder="placeholder"
      :disabled="disabled"
      :clearable="clearable"
      :show-button="showButton"
      :size="size"
      :readonly="readonly"
      :status="status"
      @update:value="handleUpdateValue"
    >
      <!-- 前缀插槽 -->
      <template v-if="$slots.prefix" #prefix>
        <slot name="prefix"></slot>
      </template>
      
      <!-- 后缀插槽 -->
      <template v-if="$slots.suffix" #suffix>
        <slot name="suffix"></slot>
      </template>
    </n-input-number>
    
    <!-- 验证状态信息显示 -->
    <div v-if="statusMessage" class="text-xs mt-1" :class="statusClass">
      {{ statusMessage }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { NInputNumber } from 'naive-ui';
import { computed } from 'vue';
import type { CSSProperties } from 'vue';

const props = defineProps({
  // 输入框的值
  value: {
    type: Number,
    default: null
  },
  // 最小值
  min: {
    type: Number,
    default: undefined
  },
  // 最大值
  max: {
    type: Number,
    default: undefined
  },
  // 步长
  step: {
    type: Number,
    default: 1
  },
  // 精度
  precision: {
    type: Number,
    default: undefined
  },
  // 占位符
  placeholder: {
    type: String,
    default: ''
  },
  // 是否禁用
  disabled: {
    type: Boolean,
    default: false
  },
  // 是否可清除
  clearable: {
    type: Boolean,
    default: false
  },
  // 是否显示按钮
  showButton: {
    type: Boolean,
    default: true
  },
  // 输入框大小
  size: {
    type: String,
    default: 'medium',
    validator: (val: string) => ['small', 'medium', 'large'].includes(val)
  },
  // 是否只读
  readonly: {
    type: Boolean,
    default: false
  },
  // 验证状态
  status: {
    type: String,
    default: undefined,
    validator: (val: string) => ['success', 'warning', 'error'].includes(val)
  },
  // 验证状态消息
  statusMessage: {
    type: String,
    default: ''
  },
  // 自定义输入框类名
  inputClass: {
    type: String,
    default: ''
  },
  // 自定义样式
  style: {
    type: [String, Object] as unknown as () => string | CSSProperties,
    default: () => ({})
  },
  // 组件容器类名
  className: {
    type: String,
    default: ''
  }
});

const emit = defineEmits(['update:value']);

// 根据状态计算文本颜色
const statusClass = computed(() => {
  if (props.status === 'error') return 'text-red-500';
  if (props.status === 'warning') return 'text-orange-500';
  if (props.status === 'success') return 'text-green-500';
  return '';
});

// 处理输入值更新
const handleUpdateValue = (value: number | null) => {
  emit('update:value', value);
};
</script>

<style scoped>
/* 可根据需要添加样式 */
</style> 