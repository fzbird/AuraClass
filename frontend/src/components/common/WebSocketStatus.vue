<template>
  <div class="ws-status">
    <n-popover trigger="click" v-model:show="showPopover" placement="bottom">
      <template #trigger>
        <div class="status-trigger" :class="{ connected: isConnected }">
          <span class="status-indicator" :class="statusClass"></span>
          <span v-if="showText" class="status-text">{{ statusText }}</span>
        </div>
      </template>
      
      <div class="status-details">
        <h3>WebSocket 状态</h3>
        <n-divider />
        
        <n-list>
          <n-list-item>
            <div class="detail-item">
              <span class="detail-label">连接状态:</span>
              <n-tag :type="isConnected ? 'success' : 'error'">
                {{ statusText }}
              </n-tag>
            </div>
          </n-list-item>
          
          <n-list-item v-if="wsStore.endpoint">
            <div class="detail-item">
              <span class="detail-label">连接端点:</span>
              <span class="detail-value endpoint">{{ wsStore.endpoint }}</span>
            </div>
          </n-list-item>
          
          <n-list-item v-if="connectionError">
            <div class="detail-item">
              <span class="detail-label">错误信息:</span>
              <span class="detail-value error-message">{{ connectionError }}</span>
            </div>
          </n-list-item>
          
          <n-list-item>
            <div class="detail-item">
              <span class="detail-label">最后连接时间:</span>
              <span class="detail-value">{{ formattedTime }}</span>
            </div>
          </n-list-item>
          
          <n-list-item>
            <div class="detail-item">
              <span class="detail-label">重连次数:</span>
              <span class="detail-value">{{ wsStore.reconnectCount }}</span>
            </div>
          </n-list-item>
          
          <n-list-item>
            <div class="detail-item">
              <span class="detail-label">消息计数:</span>
              <span class="detail-value">{{ wsStore.messageCount }}</span>
            </div>
          </n-list-item>
          
          <n-list-item>
            <div class="detail-item">
              <span class="detail-label">WebSocket启用:</span>
              <span class="detail-value">{{ wsStore.config.enabled ? '是' : '否' }}</span>
            </div>
          </n-list-item>
          
          <n-list-item>
            <div class="detail-item">
              <span class="detail-label">心跳间隔:</span>
              <span class="detail-value">{{ wsStore.config.heartbeatInterval / 1000 }}秒</span>
            </div>
          </n-list-item>
        </n-list>
        
        <n-divider />
        
        <div class="diagnostic-info" v-if="showDiagnostics">
          <h4>连接诊断</h4>
          <n-list>
            <n-list-item>
              <div class="detail-item">
                <span class="detail-label">浏览器支持:</span>
                <n-tag :type="diagnostics.browserSupport ? 'success' : 'error'">
                  {{ diagnostics.browserSupport ? '支持' : '不支持' }}
                </n-tag>
              </div>
            </n-list-item>
            
            <n-list-item>
              <div class="detail-item">
                <span class="detail-label">基础URL配置:</span>
                <n-tag :type="diagnostics.baseUrlConfigured ? 'success' : 'error'">
                  {{ diagnostics.baseUrlConfigured ? '已配置' : '未配置' }}
                </n-tag>
              </div>
            </n-list-item>
            
            <n-list-item>
              <div class="detail-item">
                <span class="detail-label">用户已登录:</span>
                <n-tag :type="diagnostics.userLoggedIn ? 'success' : 'error'">
                  {{ diagnostics.userLoggedIn ? '是' : '否' }}
                </n-tag>
              </div>
            </n-list-item>
            
            <n-list-item>
              <div class="detail-item">
                <span class="detail-label">诊断结果:</span>
                <span class="detail-value">{{ diagnostics.summary }}</span>
              </div>
            </n-list-item>
          </n-list>
        </div>
        
        <n-space justify="space-between" class="actions">
          <n-button size="small" @click="toggleDiagnostics">
            {{ showDiagnostics ? '隐藏诊断' : '显示诊断' }}
          </n-button>
          
          <n-space>
            <n-button size="small" @click="handleToggleEnabled">
              {{ wsStore.config.enabled ? '禁用' : '启用' }} WebSocket
            </n-button>
            
            <n-button 
              size="small" 
              type="primary" 
              @click="handleReconnect" 
              :disabled="!wsStore.config.enabled"
            >
              重新连接
            </n-button>
            
            <n-button size="small" @click="closePopover">
              关闭
            </n-button>
          </n-space>
        </n-space>
      </div>
    </n-popover>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { NPopover, NButton, NSpace, NList, NListItem, NDivider, NTag } from 'naive-ui';
import { useWebSocketStore } from '@/stores/websocket';
import { isWebSocketSupported, checkWebSocketSupport } from '@/services/websocket/config';
import { useUserStore } from '@/stores/user';
import { useMessage } from 'naive-ui';

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
  },
  showText: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['reconnect', 'toggle-enabled']);
const wsStore = useWebSocketStore();
const userStore = useUserStore();
const message = useMessage();
const showPopover = ref(false);
const showDiagnostics = ref(false);

const statusText = computed(() => {
  if (props.isConnecting) return '连接中...';
  return props.isConnected ? '已连接' : '未连接';
});

const statusClass = computed(() => {
  if (props.isConnecting) return 'connecting';
  return props.isConnected ? 'connected' : 'disconnected';
});

const formattedTime = computed(() => {
  if (!wsStore.lastConnectedTime) return '未连接';
  
  const date = new Date(wsStore.lastConnectedTime);
  return date.toLocaleString();
});

// 诊断信息
const diagnostics = computed(() => {
  const support = checkWebSocketSupport();
  const userLoggedIn = userStore.isLoggedIn;
  
  let summary = '';
  if (!support.supported) {
    summary = support.reason || 'WebSocket不受支持';
  } else if (!userLoggedIn) {
    summary = '用户未登录，WebSocket无法建立连接';
  } else if (!wsStore.config.enabled) {
    summary = 'WebSocket已被禁用，请启用后重试';
  } else if (!props.isConnected && props.connectionError) {
    summary = `连接错误: ${props.connectionError}`;
  } else if (props.isConnected) {
    summary = '连接正常';
  } else {
    summary = '连接已断开，请尝试重新连接';
  }
  
  return {
    browserSupport: isWebSocketSupported(),
    baseUrlConfigured: support.baseUrlConfigured,
    userLoggedIn,
    summary
  };
});

const handleReconnect = () => {
  if (!wsStore.config.enabled) {
    message.warning('WebSocket已禁用，请先启用');
    return;
  }
  
  emit('reconnect');
  message.info('正在尝试重新连接...');
  showPopover.value = false;
};

const handleToggleEnabled = () => {
  const newState = !wsStore.config.enabled;
  wsStore.updateConfig({ enabled: newState });
  emit('toggle-enabled', newState);
  message.success(`WebSocket已${newState ? '启用' : '禁用'}`);
  
  if (newState && !props.isConnected && !props.isConnecting) {
    // 如果启用后尝试重连
    setTimeout(() => {
      handleReconnect();
    }, 500);
  }
};

const toggleDiagnostics = () => {
  showDiagnostics.value = !showDiagnostics.value;
};

const closePopover = () => {
  showPopover.value = false;
};
</script>

<style scoped>
.ws-status {
  display: inline-flex;
  align-items: center;
}

.status-trigger {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.status-trigger:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.status-indicator {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.connected {
  background-color: var(--success-color, #18a058);
}

.disconnected {
  background-color: var(--error-color, #d03050);
}

.connecting {
  background-color: var(--warning-color, #f0a020);
  animation: pulse 1.5s infinite;
}

.status-text {
  font-size: 12px;
  color: var(--text-color-secondary);
}

.status-details {
  width: 350px;
  max-width: 100%;
}

.status-details h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
  text-align: center;
}

.status-details h4 {
  margin: 8px 0;
  font-size: 14px;
}

.detail-item {
  display: flex;
  align-items: baseline;
  flex-wrap: wrap;
  width: 100%;
}

.detail-label {
  font-weight: 500;
  margin-right: 8px;
  min-width: 100px;
}

.detail-value {
  word-break: break-word;
}

.detail-value.endpoint {
  font-family: monospace;
  font-size: 12px;
  background-color: rgba(0, 0, 0, 0.05);
  padding: 1px 4px;
  border-radius: 2px;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.detail-value.error-message {
  color: var(--error-color, #d03050);
}

.actions {
  margin-top: 8px;
}

.diagnostic-info {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

@keyframes pulse {
  0% { opacity: 0.6; }
  50% { opacity: 1; }
  100% { opacity: 0.6; }
}

:root.dark .status-trigger:hover {
  background-color: rgba(255, 255, 255, 0.05);
}

:root.dark .detail-value.endpoint {
  background-color: rgba(255, 255, 255, 0.1);
}
</style> 