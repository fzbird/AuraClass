<template>
  <div :class="['app-copy', className]" :style="style">
    <!-- 文本内容 -->
    <div v-if="$slots.default" class="app-copy-content">
      <slot />
    </div>
    <input v-else-if="text" ref="textInput" type="text" :value="text" class="app-copy-hidden-input" readonly />

    <!-- 复制按钮 -->
    <div class="app-copy-button" @click="copyToClipboard">
      <slot name="button">
        <n-button
          :size="size"
          :type="buttonType"
          :ghost="ghost"
          :round="round"
          :circle="circle"
          :quaternary="quaternary"
          :dashed="dashed"
          :text="textButton"
          class="app-copy-default-button"
        >
          <template #icon>
            <n-icon>
              <CopyOutlined />
            </n-icon>
          </template>
          <span v-if="!hideText">{{ buttonText }}</span>
        </n-button>
      </slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { NButton, NIcon, useMessage } from 'naive-ui';
import { CopyOutlined } from 'naive-ui';
import type { PropType, CSSProperties } from 'vue';

type ButtonType = 'default' | 'tertiary' | 'primary' | 'info' | 'success' | 'warning' | 'error';
type ButtonSize = 'tiny' | 'small' | 'medium' | 'large';

const props = defineProps({
  // 要复制的文本，会优先考虑 slot
  text: {
    type: String,
    default: ''
  },
  // 按钮文本
  buttonText: {
    type: String,
    default: '复制'
  },
  // 隐藏按钮文本，只显示图标
  hideText: {
    type: Boolean,
    default: false
  },
  // 复制成功提示
  successMessage: {
    type: String,
    default: '复制成功'
  },
  // 复制失败提示
  errorMessage: {
    type: String,
    default: '复制失败'
  },
  // 按钮类型
  buttonType: {
    type: String as PropType<ButtonType>,
    default: 'default'
  },
  // 按钮大小
  size: {
    type: String as PropType<ButtonSize>,
    default: 'small'
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
  // 是否为圆形按钮
  circle: {
    type: Boolean,
    default: false
  },
  // 是否为文本按钮
  textButton: {
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
  // 自定义样式
  style: {
    type: [String, Object] as PropType<string | CSSProperties>,
    default: null
  },
  // 自定义类名
  className: {
    type: String,
    default: ''
  }
});

const emit = defineEmits(['copy', 'success', 'error']);

// 消息服务
const message = useMessage();

// 文本输入框引用
const textInput = ref<HTMLInputElement | null>(null);

// 获取要复制的文本
const getTextToCopy = (): string => {
  // 获取插槽内容文本
  const getSlotText = (): string | null => {
    const el = document.querySelector('.app-copy-content');
    return el ? el.textContent || '' : null;
  };

  // 优先使用插槽内容
  const slotText = getSlotText();
  if (slotText !== null) {
    return slotText;
  }
  
  // 其次使用传入的文本
  return props.text || '';
};

// 复制到剪贴板
const copyToClipboard = async () => {
  try {
    const textToCopy = getTextToCopy();
    
    if (!textToCopy) {
      message.warning('没有可复制的内容');
      return;
    }
    
    emit('copy', textToCopy);

    // 使用现代 Clipboard API
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(textToCopy);
      handleSuccess();
      return;
    }

    // 回退方法: 创建临时文本区域
    const textarea = document.createElement('textarea');
    textarea.value = textToCopy;
    textarea.style.position = 'absolute';
    textarea.style.left = '-9999px';
    textarea.style.top = '-9999px';
    document.body.appendChild(textarea);
    textarea.focus();
    textarea.select();
    
    const successful = document.execCommand('copy');
    document.body.removeChild(textarea);
    
    if (successful) {
      handleSuccess();
    } else {
      handleError(new Error('execCommand 复制失败'));
    }
  } catch (error) {
    handleError(error);
  }
};

// 处理复制成功
const handleSuccess = () => {
  message.success(props.successMessage);
  emit('success');
};

// 处理复制失败
const handleError = (error: any) => {
  console.error('复制失败:', error);
  message.error(props.errorMessage);
  emit('error', error);
};

// 挂载时设置消息组件
onMounted(() => {
  // 将输入框设置为只读
  if (textInput.value) {
    textInput.value.readOnly = true;
  }
});
</script>

<style scoped>
.app-copy {
  display: inline-flex;
  align-items: center;
  position: relative;
}

.app-copy-content {
  margin-right: 8px;
}

.app-copy-hidden-input {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.app-copy-button {
  cursor: pointer;
  display: inline-flex;
  align-items: center;
}

.app-copy-default-button {
  margin-left: 4px;
}
</style> 