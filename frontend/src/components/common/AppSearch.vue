<template>
  <div :class="[className, 'app-search-wrapper']">
    <n-input
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      :size="size"
      :round="round"
      :loading="loading"
      :maxlength="maxlength"
      :clearable="clearable"
      :style="style"
      :class="[inputClass, 'app-search-input']"
      @update:value="handleUpdateValue"
      @focus="handleFocus"
      @blur="handleBlur"
      @keydown="handleKeydown"
      @clear="handleClear"
    >
      <template #prefix>
        <slot name="prefix">
          <n-icon :size="iconSize" :class="iconClass">
            <SearchOutlined />
          </n-icon>
        </slot>
      </template>
      <template #suffix>
        <slot name="suffix">
          <div v-if="loading" class="app-search-loading">
            <n-spin size="small" />
          </div>
          <n-button 
            v-else-if="showSearchButton" 
            :size="buttonSize" 
            type="primary" 
            @click="handleSearch"
            :disabled="disabled || !modelValue"
          >
            {{ searchButtonText }}
          </n-button>
        </slot>
      </template>
    </n-input>
    <div v-if="error" class="app-search-error">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { NInput, NIcon, NButton, NSpin, SearchOutlined } from 'naive-ui';
import type { CSSProperties, PropType } from 'vue';

type InputSize = 'tiny' | 'small' | 'medium' | 'large';

const props = defineProps({
  // v-model 绑定值
  modelValue: {
    type: String,
    default: ''
  },
  // 占位文本
  placeholder: {
    type: String,
    default: '搜索...'
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
  // 是否为圆角
  round: {
    type: Boolean,
    default: true
  },
  // 是否加载中
  loading: {
    type: Boolean,
    default: false
  },
  // 最大长度
  maxlength: {
    type: Number,
    default: undefined
  },
  // 是否可清空
  clearable: {
    type: Boolean,
    default: true
  },
  // 是否显示搜索按钮
  showSearchButton: {
    type: Boolean,
    default: false
  },
  // 搜索按钮文本
  searchButtonText: {
    type: String,
    default: '搜索'
  },
  // 错误信息
  error: {
    type: String,
    default: ''
  },
  // 自定义样式
  style: {
    type: [String, Object] as unknown as PropType<string | CSSProperties>,
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
  // 图标类名
  iconClass: {
    type: String,
    default: ''
  }
});

const emit = defineEmits([
  'update:modelValue',
  'search',
  'focus',
  'blur',
  'keydown',
  'clear'
]);

// 计算图标大小，根据输入框大小调整
const iconSize = computed(() => {
  switch (props.size) {
    case 'tiny': return 14;
    case 'small': return 16;
    case 'medium': return 18;
    case 'large': return 20;
    default: return 18;
  }
});

// 计算按钮大小，根据输入框大小调整
const buttonSize = computed(() => {
  switch (props.size) {
    case 'tiny': return 'tiny';
    case 'small': return 'tiny';
    case 'medium': return 'small';
    case 'large': return 'medium';
    default: return 'small';
  }
});

// 处理值更新
const handleUpdateValue = (value: string) => {
  emit('update:modelValue', value);
};

// 处理搜索
const handleSearch = () => {
  if (props.modelValue) {
    emit('search', props.modelValue);
  }
};

// 处理聚焦
const handleFocus = (e: FocusEvent) => {
  emit('focus', e);
};

// 处理失焦
const handleBlur = (e: FocusEvent) => {
  emit('blur', e);
};

// 处理按键按下
const handleKeydown = (e: KeyboardEvent) => {
  emit('keydown', e);
  // 回车键触发搜索
  if (e.key === 'Enter' && props.modelValue) {
    handleSearch();
  }
};

// 处理清空
const handleClear = (e: MouseEvent) => {
  emit('clear', e);
  emit('update:modelValue', '');
  // 清空后也触发搜索事件，传空字符串
  emit('search', '');
};
</script>

<style scoped>
.app-search-wrapper {
  position: relative;
  width: 100%;
}

.app-search-error {
  color: var(--error-color, #f5222d);
  font-size: 12px;
  line-height: 1.5;
  margin-top: 4px;
}

.app-search-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 8px;
}
</style> 