<template>
  <n-card 
    class="mb-4 notification-card"
    :class="{ 'unread-notification': !notification.is_read }"
    size="small"
    embedded
  >
    <div class="flex justify-between">
      <!-- 左侧内容区域 -->
      <div class="flex-grow pr-4" @click="handleView">
        <div class="flex items-center">
          <!-- 未读标识，放在标题左侧 -->
          <n-badge v-if="!notification.is_read" dot color="#2080f0" class="mr-2" />
          <h3 class="text-base font-medium">{{ notification.title }}</h3>
        </div>
        
        <p class="text-gray-600 text-sm line-clamp-2 mt-2">{{ notification.content }}</p>
        
        <div class="flex items-center text-xs text-gray-500 mt-2">
          <span>{{ formatDate(notification.created_at) }}</span>
          <n-divider vertical />
          <span>{{ notification.sender_name || '系统' }}</span>
        </div>
      </div>
      
      <!-- 右侧操作区域 -->
      <div class="flex items-center space-x-2 shrink-0">
        <n-button 
          v-if="!notification.is_read" 
          size="small"
          type="info"
          @click.stop="$emit('mark-read', notification.id)"
        >
          <template #icon>
            <n-icon><check-outlined /></n-icon>
          </template>
          标为已读
        </n-button>
        
        <n-button 
          size="small"
          type="error"
          :loading="isDeleting"
          @click.stop="$emit('delete', notification)"
        >
          <template #icon>
            <n-icon v-if="!isDeleting"><delete-outlined /></n-icon>
          </template>
          <n-tooltip placement="top" trigger="hover">
            <template #trigger>
              {{ isDeleting ? '删除中' : '删除' }}
            </template>
            删除权限：管理员可删除所有通知，接收者可删除个人通知，发送者仅可删除未读通知
          </n-tooltip>
        </n-button>
      </div>
    </div>
  </n-card>
</template>

<script setup lang="ts">
import { NButton, NTag, NDivider, NCard, NBadge, NIcon, NTooltip } from 'naive-ui';
import { CheckOutlined, DeleteOutlined } from '@vicons/antd';
import dayjs from 'dayjs';
import { computed } from 'vue';

interface Notification {
  id: number;
  title: string;
  content: string;
  is_read: boolean;
  created_at: string;
  sender_name?: string;
}

const props = defineProps<{
  notification: Notification;
  deletingIds?: Set<number>; // 正在删除的通知ID集合
}>();

// 计算当前通知是否正在删除中
const isDeleting = computed(() => 
  props.deletingIds && props.deletingIds.has(props.notification.id)
);

const emit = defineEmits<{
  (e: 'mark-read', id: number): void;
  (e: 'delete', notification: Notification): void;
  (e: 'view', notification: Notification): void;
}>();

const formatDate = (dateString: string): string => {
  const date = dayjs(dateString);
  const now = dayjs();
  
  if (date.isSame(now, 'day')) {
    return `今天 ${date.format('HH:mm')}`;
  } else if (date.isSame(now.subtract(1, 'day'), 'day')) {
    return `昨天 ${date.format('HH:mm')}`;
  } else if (date.isSame(now, 'year')) {
    return date.format('MM-DD HH:mm');
  } else {
    return date.format('YYYY-MM-DD HH:mm');
  }
};

const handleView = () => {
  emit('view', props.notification);
};
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.notification-card {
  transition: all 0.3s ease;
  cursor: pointer;
}

.notification-card:hover {
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.unread-notification {
  border-left: 3px solid #2080f0;
}
</style>