<template>
  <div class="notification-list">
    <div v-if="notifications.length === 0" class="empty-state">
      <div class="text-center py-4 text-gray-500">
        暂无通知
      </div>
    </div>
    
    <div v-else>
      <div
        v-for="notification in limitedNotifications"
        :key="notification.id"
        class="notification-item"
        :class="{ 'unread': !notification.isRead }"
        @click="handleClick(notification)"
      >
        <div class="flex justify-between items-start">
          <div class="font-medium truncate">{{ notification.title }}</div>
          <div class="text-xs text-gray-500 ml-2 whitespace-nowrap">
            {{ formatDateTime(notification.createdAt) }}
          </div>
        </div>
        
        <div class="text-sm text-gray-600 truncate mt-1">
          {{ notification.content }}
        </div>
        
        <div class="action-buttons flex justify-end mt-2" v-if="showActions">
          <n-button 
            v-if="!notification.isRead" 
            size="tiny" 
            quaternary
            @click.stop="markAsRead(notification.id)"
          >
            标为已读
          </n-button>
          <n-button 
            size="tiny" 
            quaternary 
            @click.stop="deleteNotification(notification.id)"
          >
            删除
          </n-button>
        </div>
      </div>
      
      <div v-if="hasMore" class="view-more text-center mt-2">
        <n-button text size="small" @click="$emit('view-more')">
          查看更多
        </n-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { NButton } from 'naive-ui';
import { useNotificationStore } from '@/stores/notification';
import { formatDateTime } from '@/utils/formatters';
import type { Notification } from '@/types/notification';

const props = defineProps({
  notifications: {
    type: Array as () => Notification[],
    default: () => []
  },
  limit: {
    type: Number,
    default: 0 // 0表示不限制
  },
  showActions: {
    type: Boolean,
    default: true
  }
});

const emit = defineEmits(['view-more', 'click']);

const notificationStore = useNotificationStore();

// 限制显示的通知数量
const limitedNotifications = computed(() => {
  if (props.limit > 0) {
    return props.notifications.slice(0, props.limit);
  }
  return props.notifications;
});

// 是否有更多通知
const hasMore = computed(() => {
  return props.limit > 0 && props.notifications.length > props.limit;
});

// 点击通知
const handleClick = (notification: Notification) => {
  emit('click', notification);
};

// 标记通知为已读
const markAsRead = async (id: number) => {
  await notificationStore.markAsRead(id);
};

// 删除通知
const deleteNotification = async (id: number) => {
  await notificationStore.remove(id);
};
</script>

<style scoped>
.notification-item {
  padding: 10px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.notification-item:hover {
  background-color: #f9f9f9;
}

.notification-item.unread {
  background-color: rgba(24, 144, 255, 0.05);
}

.notification-item.unread:hover {
  background-color: rgba(24, 144, 255, 0.1);
}

.empty-state {
  padding: 20px;
  text-align: center;
}

.action-buttons {
  opacity: 0;
  transition: opacity 0.2s ease;
}

.notification-item:hover .action-buttons {
  opacity: 1;
}
</style> 