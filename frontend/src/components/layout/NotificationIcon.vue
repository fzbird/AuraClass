<template>
  <div class="notification-icon" @click.stop>
    <n-badge 
      :value="unreadCount" 
      :max="99"
      :show-zero="false"
      color="#f5222d"
    >
      <div class="icon-wrapper" @click="togglePanel">
        <icon-notification :size="24" />
      </div>
    </n-badge>
    
    <div class="notification-panel-wrapper" v-if="showPanel">
      <notification-panel 
        v-model:show="showPanel"
        @close="showPanel = false"
      >
        <template #header-actions>
          <!-- 标记为已读 -->
          <button
            v-if="hasUnread"
            class="mark-all-read-btn"
            @click="markAllAsRead"
          >
            <icon-check :size="14" />
            <span>全部标为已读</span>
          </button>
        </template>
      </notification-panel>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import { NBadge } from 'naive-ui';
import { useNotificationStore } from '@/stores/notification';
import NotificationPanel from './NotificationPanel.vue';
import IconNotification from '@/components/icons/IconNotification.vue';
import IconCheck from '@/components/icons/IconCheck.vue';
import type { Notification } from '@/types/notification';

const notificationStore = useNotificationStore();
const showPanel = ref(false);

// 获取通知列表
const notifications = computed(() => notificationStore.notifications);
// 未读数量
const unreadCount = computed(() => notificationStore.unreadCount);
// 是否有未读通知
const hasUnread = computed(() => unreadCount.value > 0);

// 未读通知的ID列表
const unreadNotificationIds = computed(() => {
  return notificationStore.notifications
    .filter((notification: Notification) => !notification.isRead)
    .map((notification: Notification) => notification.id);
});

// 标记所有通知为已读
const markAllAsRead = () => {
  const ids = unreadNotificationIds.value;
  if (ids.length > 0) {
    // 调用store中的方法标记为已读
    ids.forEach((id: number) => notificationStore.markAsRead(id));
    showPanel.value = false;
  }
};

// 切换通知面板显示状态
const togglePanel = () => {
  showPanel.value = !showPanel.value;
};

// 点击外部关闭面板
const handleClickOutside = (event: MouseEvent) => {
  const notificationIcon = document.querySelector('.notification-icon');
  if (notificationIcon && !notificationIcon.contains(event.target as Node) && showPanel.value) {
    showPanel.value = false;
  }
};

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside);
});
</script>

<style scoped>
.notification-icon {
  position: relative;
  cursor: pointer;
}

.icon-wrapper {
  padding: 4px;
  border-radius: 50%;
  transition: background-color 0.3s;
}

.icon-wrapper:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.notification-panel-wrapper {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 8px;
  z-index: 1000;
}

.mark-all-read-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  font-size: 12px;
  color: var(--primary-color, #18a058);
  background: transparent;
  border: none;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.mark-all-read-btn:hover {
  background-color: rgba(24, 160, 88, 0.1);
}
</style> 