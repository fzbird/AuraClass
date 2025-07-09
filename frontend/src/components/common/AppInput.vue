<template>
  <div :class="[className, 'app-input-wrapper']">
    <n-input
      :value="modelValue"
      :type="type"
      :placeholder="placeholder"
      :disabled="disabled"
      :size="size"
      :status="status"
      :clearable="clearable"
      :round="round"
      :loading="loading"
      :maxlength="maxlength"
      :show-count="showCount"
      :readonly="readonly"
      :prefix="prefix"
      :suffix="suffix"
      :style="style"
      :class="inputClass"
      :autofocus="autofocus"
      :pair="pair"
      :separator="separator"
      :autocomplete="autocomplete"
      :show-password-on="showPasswordOn"
      :passively-activated="passivelyActivated"
      :input-props="inputProps"
      @update:value="handleUpdateValue"
      @focus="handleFocus"
      @blur="handleBlur"
      @change="handleChange"
      @input="handleInput"
      @keydown="handleKeydown"
      @keyup="handleKeyup"
      @clear="handleClear"
    >
      <template #prefix v-if="$slots.prefix">
        <slot name="prefix" />
      </template>
      <template #suffix v-if="$slots.suffix">
        <slot name="suffix" />
      </template>
      <template #count v-if="$slots.count">
        <slot name="count" />
      </template>
      <template #separator v-if="$slots.separator">
        <slot name="separator" />
      </template>
    </n-input>
    <div v-if="error" class="app-input-error">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
import { NInput } from 'naive-ui';
import type { CSSProperties } from 'vue';

type InputType = 'text' | 'password' | 'textarea' | 'number';
type InputSize = 'tiny' | 'small' | 'medium' | 'large';
type InputStatus = 'success' | 'warning' | 'error';
type ShowPasswordOn = 'click' | 'mousedown';

const props = defineProps({
  // v-model绑定值
  modelValue: {
    type: [String, Number, Array],
    default: ''
  },
  // 输入框类型
  type: {
    type: String as () => InputType,
    default: 'text'
  },
  // 占位文本
  placeholder: {
    type: String,
    default: ''
  },
  // 是否禁用
  disabled: {
    type: Boolean,
    default: false
  },
  // 输入框大小
  size: {
    type: String as () => InputSize,
    default: 'medium'
  },
  // 输入框状态
  status: {
    type: String as () => InputStatus,
    default: undefined
  },
  // 是否可清空
  clearable: {
    type: Boolean,
    default: false
  },
  // 是否圆角
  round: {
    type: Boolean,
    default: false
  },
  // 是否显示加载状态
  loading: {
    type: Boolean,
    default: false
  },
  // 最大字符数
  maxlength: {
    type: Number,
    default: undefined
  },
  // 是否显示字数统计
  showCount: {
    type: Boolean,
    default: false
  },
  // 是否只读
  readonly: {
    type: Boolean,
    default: false
  },
  // 前缀
  prefix: {
    type: String,
    default: undefined
  },
  // 后缀
  suffix: {
    type: String,
    default: undefined
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
  // 输入框类名
  inputClass: {
    type: String,
    default: ''
  },
  // 是否自动聚焦
  autofocus: {
    type: Boolean,
    default: false
  },
  // 是否成对输入
  pair: {
    type: Boolean,
    default: false
  },
  // 成对输入的分隔符
  separator: {
    type: String,
    default: undefined
  },
  // 自动完成
  autocomplete: {
    type: String,
    default: undefined
  },
  // 显示密码的触发方式
  showPasswordOn: {
    type: String as () => ShowPasswordOn,
    default: undefined
  },
  // 是否被动激活
  passivelyActivated: {
    type: Boolean,
    default: false
  },
  // 原生input属性
  inputProps: {
    type: Object,
    default: () => ({})
  }
});

const emit = defineEmits([
  'update:modelValue',
  'focus',
  'blur',
  'change',
  'input',
  'keydown',
  'keyup',
  'clear'
]);

// 处理值变更
const handleUpdateValue = (value: string | number | [string, string]) => {
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

// 处理变更
const handleChange = (value: string | number | [string, string]) => {
  emit('change', value);
};

// 处理输入
const handleInput = (value: string | number | [string, string]) => {
  emit('input', value);
};

// 处理按键按下
const handleKeydown = (e: KeyboardEvent) => {
  emit('keydown', e);
};

// 处理按键抬起
const handleKeyup = (e: KeyboardEvent) => {
  emit('keyup', e);
};

// 处理清空
const handleClear = (e: MouseEvent) => {
  emit('clear', e);
};
</script>

<style scoped>
.app-input-wrapper {
  position: relative;
  width: 100%;
}

.app-input-error {
  color: var(--error-color, #f5222d);
  font-size: 12px;
  line-height: 1.5;
  margin-top: 4px;
}
</style>
