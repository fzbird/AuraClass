<template>
  <n-drawer 
    :show="show" 
    :width="340" 
    placement="right"
    :auto-focus="false"
    @update:show="emit('update:show', $event)"
  >
    <n-drawer-content title="通知中心">
      <template #header>
        <div class="drawer-header">
          <span>通知中心</span>
          <div class="actions">
            <WebSocketStatus
              v-if="isWebSocketEnabled"
              :is-connected="isConnected"
              :is-connecting="isConnecting"
              :connection-error="connectionError || ''"
              @reconnect="reconnectWebsocket"
            />
            <n-button 
              v-if="hasNotifications" 
              size="small" 
              quaternary 
              @click="handleMarkAllAsRead"
            >
              全部已读
            </n-button>
          </div>
        </div>
      </template>
      
      <div class="notification-panel">
        <n-empty 
          v-if="!hasNotifications" 
          description="暂无通知" 
          size="small" 
        />
        
        <div v-else class="notification-list">
          <n-alert 
            v-if="connectionError" 
            type="warning" 
            closable 
            style="margin-bottom: 16px;"
          >
            {{ connectionError }}
          </n-alert>
          
          <n-spin :show="loading">
            <n-list>
              <n-list-item v-for="notification in notifications" :key="notification.id">
                <n-thing
                  :title="notification.title"
                  :title-extra="formatDateTime(notification.createdAt)"
                >
                  <template #avatar>
                    <div class="notification-dot" :class="{ 'unread': !notification.isRead }"></div>
                  </template>
                  
                  <div class="notification-content">
                    {{ notification.content }}
                  </div>
                  
                  <div class="notification-actions">
                    <n-button 
                      v-if="!notification.isRead" 
                      size="tiny" 
                      quaternary
                      @click="handleMarkAsRead(notification.id)"
                    >
                      标为已读
                    </n-button>
                    <n-button 
                      size="tiny" 
                      quaternary 
                      @click="handleDelete(notification.id)"
                    >
                      删除
                    </n-button>
                  </div>
                </n-thing>
              </n-list-item>
            </n-list>
          </n-spin>
          
          <n-pagination
            v-if="total > pageSize"
            :page="currentPage"
            :page-size="pageSize"
            :item-count="total"
            size="small"
            @update:page="handlePageChange"
          />
        </div>
      </div>
    </n-drawer-content>
  </n-drawer>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, onUnmounted } from 'vue';
import { 
  NDrawer, 
  NDrawerContent, 
  NList, 
  NListItem, 
  NThing, 
  NEmpty, 
  NSpin, 
  NButton,
  NPagination,
  NAlert,
  useMessage
} from 'naive-ui';
import { useNotificationStore } from '@/stores/notification';
import { formatDateTime } from '@/utils/formatters';
import { markAllNotificationsAsRead } from '@/services/api/notifications';
import { useNotificationWebSocket } from '@/services/websocket/notification';
import WebSocketStatus from '@/components/common/WebSocketStatus.vue';
import type { Notification } from '@/types/notification';
import { useWebSocketStore } from '@/stores/websocket';

const props = defineProps<{
  show: boolean
}>();

const emit = defineEmits<{
  (e: 'update:show', value: boolean): void
}>();

const message = useMessage();
const notificationStore = useNotificationStore();
const wsStore = useWebSocketStore();

// 初始化WebSocket通知服务
const { 
  isConnected, 
  isConnecting,
  connectionError, 
  sendAcknowledge, 
  reconnect,
  isWebSocketEnabled
} = useNotificationWebSocket();

const loading = computed(() => notificationStore.loading);
const notifications = computed(() => notificationStore.notifications);
const total = computed(() => notificationStore.total);
const currentPage = computed({
  get: () => notificationStore.currentPage,
  set: (value) => notificationStore.setPagination(value)
});
const pageSize = computed(() => notificationStore.pageSize);
const hasNotifications = computed(() => notifications.value.length > 0);

// 监听抽屉显示状态，当显示时获取通知
watch(() => props.show, (value) => {
  if (value) {
    notificationStore.fetchNotifications();
  }
});

// 监听WebSocket连接错误
watch(connectionError, (error) => {
  if (error && isWebSocketEnabled.value) {  // 只在WebSocket启用时才显示错误
    message.error(`通知连接错误: ${error}`);
  }
});

// 标记通知为已读
const handleMarkAsRead = async (id: number) => {
  await notificationStore.markAsRead(id);
  
  // 同时通过WebSocket发送已读确认（如果WebSocket已连接）
  if (isConnected.value && isWebSocketEnabled.value) {
    sendAcknowledge(id);
  }
  
  message.success('已标记为已读');
};

// 标记所有通知为已读
const handleMarkAllAsRead = async () => {
  try {
    await markAllNotificationsAsRead();
    
    // 更新本地数据，将所有通知标记为已读
    notifications.value.forEach((notification: Notification) => {
      if (!notification.isRead) {
        notificationStore.markAsRead(notification.id);
      }
    });
    
    message.success('已全部标记为已读');
  } catch (error) {
    message.error('操作失败，请重试');
  }
};

// 删除通知
const handleDelete = async (id: number) => {
  await notificationStore.remove(id);
  message.success('已删除通知');
};

// 处理分页
const handlePageChange = (page: number) => {
  notificationStore.fetchNotifications({ page });
};

// 重新连接WebSocket
const reconnectWebsocket = () => {
  message.info('正在尝试重新连接...');
  reconnect();
};
</script>

<style scoped>
.drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding-right: 10px;
}

.actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.notification-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.notification-list {
  flex: 1;
  overflow-y: auto;
}

.notification-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #d9d9d9;
}

.notification-dot.unread {
  background-color: #18a058;
}

.notification-content {
  margin-bottom: 8px;
  color: #666;
  font-size: 14px;
  line-height: 1.5;
}

.notification-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.connection-status-wrapper {
  margin-left: 8px;
  display: flex;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
}
</style> 