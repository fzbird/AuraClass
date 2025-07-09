<template>
  <div class="connection-status">
    <span :class="['status-indicator', statusClass]"></span>
    <span class="status-text">{{ statusText }}</span>
    
    <n-popover trigger="click" v-model:show="showPopover" placement="bottom">
      <template #trigger>
        <button class="info-button" @click="showPopover = true">
          <IconInfo size="16" color="none" />
        </button>
      </template>
      
      <div class="connection-details">
        <h3>WebSocket连接详情</h3>
        <n-divider />
        
        <n-list>
          <n-list-item>
            <span class="detail-label">连接状态:</span>
            <n-tag :type="props.isConnected ? 'success' : 'error'">
              {{ statusText }}
            </n-tag>
          </n-list-item>
          
          <n-list-item>
            <span class="detail-label">连接端点:</span>
            <span>{{ connectionEndpoint }}</span>
          </n-list-item>
          
          <n-list-item v-if="props.connectionError">
            <span class="detail-label">错误信息:</span>
            <span class="error-text">{{ props.connectionError }}</span>
          </n-list-item>
          
          <n-list-item>
            <span class="detail-label">最后连接时间:</span>
            <span>{{ formattedTime }}</span>
          </n-list-item>
          
          <n-list-item>
            <span class="detail-label">重连次数:</span>
            <span>{{ wsStore.reconnectCount }}</span>
          </n-list-item>
          
          <n-list-item>
            <span class="detail-label">消息计数:</span>
            <span>{{ wsStore.messageCount }}</span>
          </n-list-item>
          
          <n-list-item>
            <span class="detail-label">心跳间隔:</span>
            <span>{{ wsStore.config.heartbeatInterval }}ms</span>
          </n-list-item>
        </n-list>
        
        <n-divider />
        
        <n-space justify="end">
          <n-button size="small" @click="handleReconnect" :disabled="props.isConnected">
            重新连接
          </n-button>
          <n-button size="small" @click="closePopover">
            关闭
          </n-button>
        </n-space>
      </div>
    </n-popover>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { NPopover, NButton, NSpace, NList, NListItem, NDivider, NTag } from 'naive-ui';
import { useWebSocketStore } from '@/stores/websocket';
import IconInfo from '@/components/icons/IconInfo.vue';

const props = defineProps({
  isConnected: {
    type: Boolean,
    default: false
  },
  isConnecting: {
    type: Boolean,
    default: false
  },
  connectionError: {
    type: String,
    default: null
  }
});

const emit = defineEmits(['reconnect']);
const wsStore = useWebSocketStore();
const showPopover = ref(false);

const statusText = computed(() => {
  if (props.isConnecting) return '连接中...';
  return props.isConnected ? '已连接' : '未连接';
});

const statusClass = computed(() => {
  if (props.isConnecting) return 'connecting';
  return props.isConnected ? 'connected' : 'disconnected';
});

const connectionEndpoint = computed(() => {
  return wsStore.endpoint || '未设置';
});

const formattedTime = computed(() => {
  if (!wsStore.lastConnectedTime) return '未连接';
  
  const date = new Date(wsStore.lastConnectedTime);
  return date.toLocaleString();
});

const handleReconnect = () => {
  emit('reconnect');
  showPopover.value = false;
};

const closePopover = () => {
  showPopover.value = false;
};
</script>

<style scoped>
.connection-status {
  display: flex;
  align-items: center;
  gap: 4px;
}

.status-indicator {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.connected {
  background-color: #18a058;
}

.disconnected {
  background-color: #d03050;
}

.connecting {
  background-color: #f0a020;
  animation: pulse 1.5s infinite;
}

.status-text {
  font-size: 12px;
  color: var(--text-color-secondary);
}

.info-button {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  margin-left: 4px;
  display: flex;
  align-items: center;
  color: var(--text-color-secondary);
}

.info-button:hover {
  color: var(--primary-color);
}

.connection-details {
  width: 300px;
  max-width: 100%;
}

.connection-details h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
}

.detail-label {
  font-weight: 500;
  margin-right: 8px;
}

.error-text {
  color: #d03050;
}

@keyframes pulse {
  0% { opacity: 0.6; }
  50% { opacity: 1; }
  100% { opacity: 0.6; }
}
</style> 