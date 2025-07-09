<template>
  <n-card title="WebSocket诊断" class="websocket-diagnostic">
    <template #header-extra>
      <n-tooltip trigger="hover">
        <template #trigger>
          <n-button quaternary circle size="small">
            <n-icon><info-icon /></n-icon>
          </n-button>
        </template>
        本组件可用于诊断WebSocket连接问题
      </n-tooltip>
    </template>
    
    <div class="diagnostic-content">
      <n-descriptions :column="1" label-placement="left" bordered>
        <n-descriptions-item label="WebSocket功能">
          <n-tag :type="wsConfig.enabled ? 'success' : 'default'">
            {{ wsConfig.enabled ? '已启用' : '已禁用' }}
          </n-tag>
        </n-descriptions-item>
        
        <n-descriptions-item label="连接状态" v-if="wsConfig.enabled">
          <n-tag :type="wsStore.isConnected ? 'success' : wsStore.isConnecting ? 'warning' : 'error'">
            {{ wsStore.isConnected ? '已连接' : wsStore.isConnecting ? '连接中' : '未连接' }}
          </n-tag>
        </n-descriptions-item>
        
        <n-descriptions-item label="WebSocket端点" v-if="wsConfig.enabled">
          <span>{{ wsStore.endpoint || '未设置' }}</span>
        </n-descriptions-item>
        
        <n-descriptions-item label="服务器可用性" v-if="wsConfig.enabled">
          <n-tag :type="serverAvailable === null ? 'default' : serverAvailable ? 'success' : 'error'">
            {{ serverAvailable === null ? '未测试' : serverAvailable ? '可用' : '不可用' }}
          </n-tag>
        </n-descriptions-item>
        
        <n-descriptions-item label="连接错误" v-if="wsConfig.enabled && wsStore.connectionError">
          <span class="error-text">{{ wsStore.connectionError }}</span>
        </n-descriptions-item>
        
        <n-descriptions-item label="心跳间隔">
          {{ wsConfig.heartbeatInterval / 1000 }}秒
        </n-descriptions-item>
        
        <n-descriptions-item label="重连设置">
          最大{{ wsConfig.reconnectAttempts }}次，间隔{{ wsConfig.reconnectInterval / 1000 }}秒
        </n-descriptions-item>
      </n-descriptions>
      
      <div class="action-buttons">
        <n-space>
          <n-button 
            :disabled="!wsConfig.enabled" 
            @click="testServerAvailability" 
            :loading="testing"
          >
            测试服务器可用性
          </n-button>
          
          <n-button 
            :disabled="!wsConfig.enabled || !serverAvailable" 
            @click="handleReconnect" 
            :loading="wsStore.isConnecting"
          >
            重新连接
          </n-button>
          
          <n-button 
            type="primary" 
            @click="handleToggleWebSocket"
            :loading="toggling"
          >
            {{ wsConfig.enabled ? '禁用WebSocket' : '启用WebSocket' }}
          </n-button>
        </n-space>
      </div>
    </div>
  </n-card>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { 
  NCard, 
  NDescriptions, 
  NDescriptionsItem, 
  NTag, 
  NButton, 
  NSpace,
  NIcon,
  NTooltip,
  useMessage
} from 'naive-ui';
import { useWebSocketStore } from '@/stores/websocket';
import wsConfig from '@/services/websocket/config';
import { checkWebSocketAvailability, toggleWebSocketFeature } from '@/services/api/settings';
import InfoIcon from '@/components/icons/IconInfo.vue';

const message = useMessage();
const wsStore = useWebSocketStore();

// 状态管理
const serverAvailable = ref<boolean | null>(null);
const testing = ref(false);
const toggling = ref(false);

// 测试服务器可用性
const testServerAvailability = async () => {
  testing.value = true;
  try {
    serverAvailable.value = await checkWebSocketAvailability();
    if (serverAvailable.value) {
      message.success('WebSocket服务可用');
    } else {
      message.error('WebSocket服务不可用');
    }
  } catch (error) {
    serverAvailable.value = false;
    message.error('测试失败，无法连接到服务器');
  } finally {
    testing.value = false;
  }
};

// 重新连接
const handleReconnect = () => {
  if (wsStore.isConnected) {
    wsStore.reset();
  }
  message.info('正在尝试重新连接...');
  // 手动触发连接事件
  setTimeout(() => {
    // 通过修改enabled状态触发watch重连
    const original = wsConfig.enabled;
    wsConfig.enabled = false;
    setTimeout(() => {
      wsConfig.enabled = original;
    }, 100);
  }, 100);
};

// 启用/禁用WebSocket
const handleToggleWebSocket = async () => {
  toggling.value = true;
  try {
    const success = await toggleWebSocketFeature(!wsConfig.enabled);
    if (success) {
      message.success(`WebSocket已${wsConfig.enabled ? '启用' : '禁用'}`);
      if (wsConfig.enabled) {
        serverAvailable.value = true; // 启用成功意味着服务器可用
      }
    } else {
      message.error('操作失败，请重试');
    }
  } catch (error) {
    message.error('操作出错，请重试');
  } finally {
    toggling.value = false;
  }
};

// 初始化时检查服务器可用性
onMounted(async () => {
  if (wsConfig.enabled) {
    await testServerAvailability();
  }
});
</script>

<style scoped>
.websocket-diagnostic {
  margin-bottom: 20px;
}

.diagnostic-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.action-buttons {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.error-text {
  color: #d03050;
}
</style> 