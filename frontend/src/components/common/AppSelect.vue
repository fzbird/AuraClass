<template>
  <div :class="[className, 'app-select-wrapper']">
    <n-select
      :value="modelValue"
      :options="options"
      :placeholder="placeholder"
      :disabled="disabled"
      :size="size"
      :status="status"
      :filterable="filterable"
      :clearable="clearable"
      :loading="loading"
      :multiple="multiple"
      :max-tag-count="maxTagCount"
      :remote="remote"
      :remote-method="remoteMethod"
      :consistent-menu-width="consistentMenuWidth"
      :tag="tag"
      :style="style"
      :class="selectClass"
      :virtual-scroll="virtualScroll"
      :default-value="defaultValue"
      @update:value="handleUpdateValue"
      @focus="handleFocus"
      @blur="handleBlur"
      @search="handleSearch"
      @clear="handleClear"
      @update:show="handleShowChange"
    >
      <template #empty v-if="$slots.empty">
        <slot name="empty" />
      </template>
      <template #action v-if="$slots.action">
        <slot name="action" />
      </template>
      <template #arrow v-if="$slots.arrow">
        <slot name="arrow" />
      </template>
      <template #prefix v-if="$slots.prefix">
        <slot name="prefix" />
      </template>
    </n-select>
    <div v-if="error" class="app-select-error">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
import { NSelect } from 'naive-ui';
import type { CSSProperties, PropType } from 'vue';

type SelectOption = {
  label: string;
  value: string | number;
  disabled?: boolean;
  [key: string]: any;
};

type SelectSize = 'small' | 'medium' | 'large';
type SelectStatus = 'success' | 'warning' | 'error';

const props = defineProps({
  // v-model绑定值
  modelValue: {
    type: [String, Number, Array, Object],
    default: null
  },
  // 下拉选项
  options: {
    type: Array as PropType<SelectOption[]>,
    default: () => []
  },
  // 占位文本
  placeholder: {
    type: String,
    default: '请选择'
  },
  // 是否禁用
  disabled: {
    type: Boolean,
    default: false
  },
  // 选择器大小
  size: {
    type: String as () => SelectSize,
    default: 'medium'
  },
  // 选择器状态
  status: {
    type: String as () => SelectStatus,
    default: undefined
  },
  // 是否可过滤
  filterable: {
    type: Boolean,
    default: false
  },
  // 是否可清空
  clearable: {
    type: Boolean,
    default: false
  },
  // 是否显示加载状态
  loading: {
    type: Boolean,
    default: false
  },
  // 是否多选
  multiple: {
    type: Boolean,
    default: false
  },
  // 最多显示标签数量
  maxTagCount: {
    type: Number,
    default: undefined
  },
  // 是否远程搜索
  remote: {
    type: Boolean,
    default: false
  },
  // 远程搜索方法
  remoteMethod: {
    type: Function,
    default: undefined
  },
  // 菜单宽度是否与选择器同宽
  consistentMenuWidth: {
    type: Boolean,
    default: true
  },
  // 是否显示标签
  tag: {
    type: Boolean,
    default: false
  },
  // 错误信息
  error: {
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
  },
  // 选择器类名
  selectClass: {
    type: String,
    default: ''
  },
  // 是否启用虚拟滚动
  virtualScroll: {
    type: Boolean,
    default: false
  },
  // 默认值
  defaultValue: {
    type: [String, Number, Array, Object],
    default: null
  }
});

const emit = defineEmits([
  'update:modelValue',
  'focus',
  'blur',
  'search',
  'clear',
  'update:show'
]);

// 处理值变更
const handleUpdateValue = (value: string | number | Array<string | number>) => {
  emit('update:modelValue', value);
};

// 处理聚焦
const handleFocus = (e: FocusEvent) => {
  emit('focus', e);
};

// 处理失焦
const handleBlur = (e: FocusEvent) => {
  emit('blur', e);
};

// 处理搜索
const handleSearch = (value: string) => {
  emit('search', value);
};

// 处理清空
const handleClear = () => {
  emit('clear');
};

// 处理下拉框显示状态变化
const handleShowChange = (show: boolean) => {
  emit('update:show', show);
};
</script>

<style scoped>
.app-select-wrapper {
  position: relative;
  width: 100%;
}

.app-select-error {
  color: var(--error-color, #f5222d);
  font-size: 12px;
  line-height: 1.5;
  margin-top: 4px;
}
</style> 