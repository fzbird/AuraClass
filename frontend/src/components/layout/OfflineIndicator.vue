<template>
  <div class="offline-indicator">
    <n-popover trigger="hover" placement="bottom">
      <template #trigger>
        <n-badge 
          :dot="pendingSyncItems > 0" 
          :type="getBadgeType()" 
          processing
        >
          <n-button 
            quaternary 
            circle 
            size="small"
            @click="showOfflineSettingsModal = true"
          >
            <template #icon>
              <n-icon>
                <component :is="getNetworkIcon()" />
              </n-icon>
            </template>
          </n-button>
        </n-badge>
      </template>
      <div style="padding: 4px 12px; max-width: 240px;">
        <p>{{ getNetworkStatusText() }}</p>
        <div v-if="pendingSyncItems > 0" class="mt-2">
          <p class="text-warning">{{ pendingSyncItems }} 个待同步项</p>
          <n-button 
            v-if="isOnline" 
            size="tiny" 
            type="primary" 
            class="mt-1"
            :loading="syncState === 'syncing'"
            @click="syncNow"
          >
            立即同步
          </n-button>
        </div>
      </div>
    </n-popover>
    
    <!-- 离线设置模态框 -->
    <n-modal v-model:show="showOfflineSettingsModal" preset="card" title="离线模式设置">
      <n-space vertical>
        <n-alert 
          :type="isOnline ? 'info' : 'warning'"
          :title="isOnline ? '当前已连接网络' : '当前处于离线状态'"
        >
          <p>{{ isOnline ? '网络连接正常，所有功能可用' : '网络连接不可用，部分功能可能受限' }}</p>
        </n-alert>
        
        <n-switch 
          v-model:value="offlineModeEnabled" 
          @update:value="toggleOfflineMode"
        >
          <template #checked>启用离线模式</template>
          <template #unchecked>禁用离线模式</template>
        </n-switch>
        
        <n-divider />
        
        <div class="offline-settings">
          <h3 class="text-lg mb-2">离线数据</h3>
          
          <div class="offline-stats mb-4">
            <div class="stat-item">
              <span class="stat-label">待同步项：</span>
              <span class="stat-value">{{ pendingSyncItems }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">上次同步：</span>
              <span class="stat-value">{{ getLastSyncTimeText() }}</span>
            </div>
          </div>
          
          <n-space>
            <n-button 
              type="primary" 
              :disabled="!isOnline || pendingSyncItems === 0 || syncState === 'syncing'"
              :loading="syncState === 'syncing'"
              @click="syncNow"
            >
              <template #icon>
                <n-icon><cloud-upload-outlined /></n-icon>
              </template>
              同步所有数据
            </n-button>
            
            <n-button 
              type="error" 
              :disabled="pendingSyncItems === 0"
              @click="confirmClearOfflineData"
            >
              <template #icon>
                <n-icon><delete-outlined /></n-icon>
              </template>
              清空离线数据
            </n-button>
          </n-space>
          
          <div v-if="syncState === 'syncing'" class="sync-progress mt-4">
            <n-progress 
              type="line" 
              :percentage="syncProgress" 
              :indicator-placement="'inside'"
              :processing="true"
            />
            <p class="text-sm mt-1 text-secondary">正在同步数据 ({{ syncProgress }}%)</p>
          </div>
        </div>
      </n-space>
    </n-modal>
    
    <!-- 清空确认对话框 -->
    <n-modal v-model:show="showClearConfirmModal" preset="dialog" title="确认清空离线数据" 
      type="warning" 
      :show-icon="true"
      negative-text="取消"
      positive-text="确认清空"
      @positive-click="clearOfflineData"
    >
      <template #default>
        <p>您确定要清空所有离线数据吗？这将删除所有尚未同步的更改，此操作不可撤销。</p>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import {
  NPopover,
  NBadge,
  NButton,
  NIcon,
  NSpace,
  NAlert,
  NSwitch,
  NDivider,
  NModal,
  NProgress,
  useMessage,
  useDialog
} from 'naive-ui';
import WifiOutlined from '@vicons/antd/es/WifiOutlined';
import DisconnectOutlined from '@vicons/antd/es/DisconnectOutlined';
import CloudOutlined from '@vicons/antd/es/CloudOutlined';
import CloudUploadOutlined from '@vicons/antd/es/CloudUploadOutlined';
import DeleteOutlined from '@vicons/antd/es/DeleteOutlined';
import { 
  useNetworkStatus, 
  syncOfflineData, 
  clearOfflineData as clearOfflineDataUtil, 
  isOnline, 
  offlineEnabled, 
  syncState, 
  syncProgress, 
  lastSyncTime, 
  pendingSyncItems 
} from '@/utils/offline';

const props = defineProps({
  showPendingCount: {
    type: Boolean,
    default: true
  }
});

const emit = defineEmits(['sync-start', 'sync-complete', 'sync-error']);

const message = useMessage();
const dialog = useDialog();
const { toggleOfflineMode } = useNetworkStatus();

const showOfflineSettingsModal = ref(false);
const showClearConfirmModal = ref(false);

// 计算属性：离线模式启用状态
const offlineModeEnabled = computed({
  get: () => offlineEnabled.value,
  set: (value) => toggleOfflineMode(value)
});

// 获取网络状态图标
const getNetworkIcon = () => {
  if (!isOnline.value) {
    return DisconnectOutlined;
  }
  
  if (pendingSyncItems.value > 0) {
    return CloudOutlined;
  }
  
  return WifiOutlined;
};

// 获取网络状态文本
const getNetworkStatusText = () => {
  if (!isOnline.value) {
    return offlineEnabled.value
      ? '当前处于离线模式，您的操作将在恢复连接后自动同步'
      : '网络连接已断开，部分功能可能不可用';
  }
  
  if (pendingSyncItems.value > 0) {
    return `有 ${pendingSyncItems.value} 个操作等待同步`;
  }
  
  return '网络连接正常';
};

// 获取上次同步时间文本
const getLastSyncTimeText = () => {
  if (!lastSyncTime.value) {
    return '从未同步';
  }
  
  // 格式化时间，如 "今天 12:30" 或 "2023-01-01 12:30"
  const now = new Date();
  const syncDate = lastSyncTime.value;
  
  const isSameDay = 
    now.getFullYear() === syncDate.getFullYear() &&
    now.getMonth() === syncDate.getMonth() &&
    now.getDate() === syncDate.getDate();
  
  if (isSameDay) {
    return `今天 ${syncDate.getHours().toString().padStart(2, '0')}:${syncDate.getMinutes().toString().padStart(2, '0')}`;
  }
  
  return `${syncDate.getFullYear()}-${(syncDate.getMonth() + 1).toString().padStart(2, '0')}-${syncDate.getDate().toString().padStart(2, '0')} ${syncDate.getHours().toString().padStart(2, '0')}:${syncDate.getMinutes().toString().padStart(2, '0')}`;
};

// 获取徽章类型
const getBadgeType = () => {
  if (!isOnline.value) {
    return 'error';
  }
  
  if (pendingSyncItems.value > 0) {
    return 'warning';
  }
  
  return 'success';
};

// 立即同步数据
const syncNow = async () => {
  if (!isOnline.value || syncState.value === 'syncing') {
    return;
  }
  
  emit('sync-start');
  
  try {
    const success = await syncOfflineData();
    
    if (success) {
      message.success('数据同步成功');
      emit('sync-complete', { success: true });
    } else {
      message.error('部分数据同步失败，请稍后重试');
      emit('sync-complete', { success: false });
    }
  } catch (error) {
    console.error('Sync error:', error);
    message.error('同步过程中发生错误');
    emit('sync-error', error);
  }
};

// 确认清空离线数据
const confirmClearOfflineData = () => {
  showClearConfirmModal.value = true;
};

// 清空离线数据
const clearOfflineData = () => {
  clearOfflineDataUtil();
  message.success('离线数据已清空');
};
</script>

<style scoped>
.offline-indicator {
  display: inline-flex;
  align-items: center;
}

.text-warning {
  color: #f0a020;
}

.text-secondary {
  color: #606266;
}

.text-lg {
  font-size: 16px;
  font-weight: 500;
}

.mt-1 {
  margin-top: 4px;
}

.mt-2 {
  margin-top: 8px;
}

.mt-4 {
  margin-top: 16px;
}

.mb-2 {
  margin-bottom: 8px;
}

.mb-4 {
  margin-bottom: 16px;
}

.offline-stats {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-item {
  display: flex;
}

.stat-label {
  width: 80px;
  color: #606266;
}

.sync-progress {
  width: 100%;
}

.text-sm {
  font-size: 12px;
}
</style> 