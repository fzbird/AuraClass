<template>
  <div v-if="errorMessage" class="error-message" :class="$attrs.class">
    <div class="error-content">
      <div class="error-header">
        <h3 v-if="title" class="error-title">{{ title }}</h3>
        <h3 v-else class="error-title">错误信息</h3>
        <button v-if="closable" class="close-button" @click="handleClose">
          &times;
        </button>
      </div>
      <div class="error-body">
        {{ errorMessage }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps({
  error: {
    type: [String, Error, Object, null],
    default: null
  },
  title: {
    type: String,
    default: ''
  },
  closable: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['close']);

// 提取错误消息
const errorMessage = computed(() => {
  if (!props.error) {
    return '';
  }
  
  if (typeof props.error === 'string') {
    return props.error;
  }
  
  if (props.error instanceof Error) {
    return props.error.message;
  }
  
  if (typeof props.error === 'object' && props.error !== null) {
    // 尝试获取对象中的message或msg属性
    return props.error.message || props.error.msg || JSON.stringify(props.error);
  }
  
  return String(props.error);
});

const handleClose = () => {
  emit('close');
};
</script>

<style scoped>
.error-message {
  background-color: #fef0f0;
  border: 1px solid #fde2e2;
  border-radius: 4px;
  padding: 12px;
  margin-bottom: 16px;
  color: #f56c6c;
}

.error-content {
  display: flex;
  flex-direction: column;
}

.error-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.error-title {
  font-size: 14px;
  font-weight: 600;
  margin: 0;
}

.close-button {
  background: none;
  border: none;
  color: #c0c4cc;
  cursor: pointer;
  font-size: 18px;
  line-height: 1;
  padding: 0;
}

.close-button:hover {
  color: #909399;
}

.error-body {
  font-size: 14px;
  line-height: 1.5;
}

/* 深色模式支持 */
:deep(.n-config-provider.n-theme-dark) .error-message {
  background-color: #4d3030;
  border-color: #5e3333;
  color: #f89898;
}
</style> 