<template>
  <div>
    <!-- 通知由 Naive UI 的 useMessage 提供 -->
  </div>
</template>

<script setup lang="ts">
import { watch } from 'vue';
import { useAppStore } from '@/stores/app';
import { useMessage } from 'naive-ui';

const appStore = useAppStore();
const message = useMessage();

// 监听通知状态，显示消息
watch(() => appStore.notification.show, (show) => {
  if (show) {
    const { type, message: content } = appStore.notification;
    
    switch (type) {
      case 'success':
        message.success(content);
        break;
      case 'info':
        message.info(content);
        break;
      case 'warning':
        message.warning(content);
        break;
      case 'error':
        message.error(content);
        break;
      default:
        message.info(content);
    }
  }
});
</script>
